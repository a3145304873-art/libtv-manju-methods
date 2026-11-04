// English story canvas plugin: exposes the local english-story CLI as four agent tools.
// No network, no Monet import, no media generation. It only reads/writes workspace files.

export const name = 'english-story'
export const inject = ['tools', 'subprocess']

const DEFAULT_WORKSPACE = 'E:\\libtv漫剧\\08_作品\\_共享工具\\english-story'

const RESULT_SCHEMA = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['pass', 'warn', 'fail', 'error'] },
    exitCode: { type: 'number' },
    stdout: { type: 'string' },
    stderr: { type: 'string' },
    artifact: { type: 'string' },
  },
  required: ['status', 'exitCode', 'stdout'],
  additionalProperties: false,
}

export function apply(ctx, config = {}) {
  const settings = config && typeof config === 'object' ? config : {}
  const workspace = typeof settings.workspace === 'string' && settings.workspace
    ? settings.workspace
    : DEFAULT_WORKSPACE
  const python = typeof settings.python === 'string' && settings.python ? settings.python : 'py'
  const pythonArgs = Array.isArray(settings.pythonArgs) && settings.pythonArgs.length > 0
    ? settings.pythonArgs.map(String)
    : ['-3']

  const statusOf = (code) => (code === 0 ? 'pass' : code === 1 ? 'warn' : code === 2 ? 'fail' : 'error')

  const output = {
    schema: RESULT_SCHEMA,
    render(_args, value) {
      try {
        if (!value || typeof value !== 'object') return [{ type: 'text', text: 'no result' }]
        const lines = [`[${value.status}] exit ${value.exitCode}`]
        if (value.artifact) lines.push(`artifact: ${value.artifact}`)
        if (value.stdout) lines.push(String(value.stdout).trim().slice(0, 6000))
        if (value.stderr) lines.push('stderr:\n' + String(value.stderr).trim().slice(0, 3000))
        return [{ type: 'text', text: lines.join('\n') }]
      } catch (error) {
        return [{ type: 'text', text: `render failed: ${error instanceof Error ? error.message : String(error)}` }]
      }
    },
  }

  async function runCli(exec, argv) {
    let handle
    try {
      handle = ctx.subprocess.spawn({
        argv: [python, ...pythonArgs, 'cli.py', ...argv],
        cwd: workspace,
        stdio: {
          stdin: 'ignore',
          stdout: { maxBytes: 512000, spill: { maxBytes: 4194304 } },
          stderr: { maxBytes: 64000 },
        },
        graceMs: 5000,
        signal: exec.signal,
      })
    } catch (error) {
      return {
        status: 'error',
        exitCode: -1,
        stdout: '',
        stderr: `spawn failed: ${error instanceof Error ? error.message : String(error)}`,
      }
    }

    let outcome
    try {
      outcome = await handle.done
    } catch (error) {
      return {
        status: 'error',
        exitCode: -1,
        stdout: '',
        stderr: `run failed: ${error instanceof Error ? error.message : String(error)}`,
      }
    }

    const read = (reader) => {
      if (!reader) return ''
      try {
        const chunk = reader.readFrom(0)
        return chunk && typeof chunk.text === 'string' ? chunk.text : ''
      } catch {
        return ''
      }
    }

    const exitCode = typeof outcome.exitCode === 'number' ? outcome.exitCode : -1
    return {
      status: statusOf(exitCode),
      exitCode,
      stdout: read(handle.collected.stdout),
      stderr: read(handle.collected.stderr),
    }
  }

  const baseName = (p) => String(p).replace(/\\/g, '/').split('/').pop().replace(/\.json$/i, '')
  const cleanDir = (p) => String(p).replace(/\\/g, '/').replace(/\/+$/, '')

  const tools = [
    {
      name: 'english_story_brief',
      description:
        '生成玩梗学单词短剧任务书：比较自然谐音、词形/词族联想等记忆梗，要求笑点把英文词和准确词义钩在一起；不写成课堂讲解。只写任务书，不建画布、不生成素材。',
      parameters: {
        type: 'object',
        properties: {
          word: { type: 'string', description: '目标英语单词，如 pest' },
          zh: { type: 'string', description: '可选的中文谐音/联想短句；留空时在任务书中按创意方向决定' },
          meaning: { type: 'string', description: '中文词义，如 害虫' },
          ipa: { type: 'string', description: '音标，可选，如 /pest/' },
          scene: { type: 'string', description: '场景偏好，可选，如 夏夜小院石桌' },
          profile: {
            type: 'string',
            enum: ['harmonic15', 'meme20'],
            description: '结构档：harmonic15（15s 六拍+单卡，默认）或 meme20（20s V1+V2+单卡，仅校验）',
          },
        },
        required: ['word', 'meaning'],
        additionalProperties: false,
      },
      timeoutMs: 60000,
      isConcurrencySafe: () => true,
      async execute(args, exec) {
        const a = args && typeof args === 'object' ? args : {}
        const profile = typeof a.profile === 'string' && a.profile ? a.profile : 'harmonic15'
        const argv = ['brief', '--word', String(a.word), '--meaning', String(a.meaning), '--profile', profile]
        if (a.zh) argv.push('--zh', String(a.zh))
        if (a.ipa) argv.push('--ipa', String(a.ipa))
        if (a.scene) argv.push('--scene', String(a.scene))
        const result = await runCli(exec, argv)
        return { ...result, artifact: `out/${String(a.word)}-${profile}.brief.md` }
      },
    },
    {
      name: 'english_story_validate',
      description:
        '校验 story.json：英语词条来源、候选记忆梗是否连接到准确词义并落入具体拍点、时间轴、道具首帧、角色台词和卡尾；心易只允许固定拟声“咔啵”。创意自评分数不作阻断门槛。exit 2 表示有客观阻断项，不得建画布。',
      parameters: {
        type: 'object',
        properties: {
          story: { type: 'string', description: 'story.json 路径，相对插件工作目录（如 stories/pest-15s.json）或绝对路径' },
        },
        required: ['story'],
        additionalProperties: false,
      },
      timeoutMs: 60000,
      isConcurrencySafe: () => true,
      async execute(args, exec) {
        const a = args && typeof args === 'object' ? args : {}
        return await runCli(exec, ['validate', '--story', String(a.story)])
      },
    },
    {
      name: 'english_story_build',
      description:
        '建英语玩梗短剧画布：先跑故事层门禁，再生成 .monet 的节点/边/组、逐拍 prompt、SRT 和校验报告。' +
        '含三格分镜图闸门（G1）。不导入 Monet、不生成图片或视频。',
      parameters: {
        type: 'object',
        properties: {
          story: { type: 'string', description: 'story.json 路径' },
          prefix: { type: 'string', description: '节点 ID 前缀，默认 story id；返修同步必须沿用同一前缀' },
          outDir: { type: 'string', description: '输出目录，默认 out' },
          copyTo: { type: 'string', description: '额外复制 .monet 到哪个目录，如 Downloads' },
        },
        required: ['story'],
        additionalProperties: false,
      },
      timeoutMs: 120000,
      isConcurrencySafe: () => false,
      async execute(args, exec) {
        const a = args && typeof args === 'object' ? args : {}
        const argv = ['build', '--story', String(a.story)]
        if (a.prefix) argv.push('--prefix', String(a.prefix))
        if (a.outDir) argv.push('--out-dir', String(a.outDir))
        if (a.copyTo) argv.push('--copy-to', String(a.copyTo))
        const result = await runCli(exec, argv)
        const dir = a.outDir ? cleanDir(a.outDir) : 'out'
        return { ...result, artifact: `${dir}/${baseName(a.story)}.monet` }
      },
    },
    {
      name: 'english_story_check',
      description:
        '复检画布门禁：引用双接入、禁止边、组内依赖、mainOutputId、组框重叠、三格分镜图闸门，' +
        '以及 prompt 的角色锁/负向范围/手/道具/字数/时长。exit 2 表示有阻断项，不得导入。',
      parameters: {
        type: 'object',
        properties: {
          canvas: { type: 'string', description: '.monet 路径' },
          story: { type: 'string', description: 'story.json 路径，可选；带上才能查道具、场景状态和时长' },
        },
        required: ['canvas'],
        additionalProperties: false,
      },
      timeoutMs: 60000,
      isConcurrencySafe: () => true,
      async execute(args, exec) {
        const a = args && typeof args === 'object' ? args : {}
        const argv = ['check', '--canvas', String(a.canvas)]
        if (a.story) argv.push('--story', String(a.story))
        const result = await runCli(exec, argv)
        return { ...result, artifact: String(a.canvas) }
      },
    },
  ]

  for (const tool of tools) {
    ctx.effect(() => ctx.tools.register({ ...tool, output }))
  }
}
