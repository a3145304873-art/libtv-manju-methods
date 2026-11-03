import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";

export const name = "cookline";
export const inject = ["tools", "workingDirectory"];

const TIMEOUT_MS = 180_000;
const MAX_OUTPUT = 30_000;
const ROOT_HINT = "08_作品/_共享工具/cookline/run.py";

function locateRunPy(cwd, root) {
  const tried = [];
  if (root) {
    tried.push(join(root, "run.py"));
    tried.push(join(root, "08_作品", "_共享工具", "cookline", "run.py"));
    tried.push(join(root, "cookline", "run.py"));
  }
  let dir = resolve(cwd || process.cwd());
  for (;;) {
    tried.push(join(dir, "08_作品", "_共享工具", "cookline", "run.py"));
    if (basename(dir) === "cookline") tried.push(join(dir, "run.py"));
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  for (const path of tried) {
    if (existsSync(path)) return path;
  }
  throw new Error(
    `找不到 cookline 的 run.py。从 ${resolve(cwd || process.cwd())} 向上都没有 ${ROOT_HINT}；` +
      "请把 root 指向方法库根目录（包含 08_作品 的那一层）。",
  );
}

function spawnOnce(exe, args, { cwd, signal }) {
  return new Promise((settle, fail) => {
    if (signal?.aborted) {
      fail(new Error("cookline: cancelled before start"));
      return;
    }
    const child = spawn(exe, args, {
      cwd,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let out = "";
    let err = "";
    let timedOut = false;
    let aborted = false;
    let settled = false;
    const cleanup = () => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", onAbort);
    };
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      cleanup();
      fn(value);
    };
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill();
    }, TIMEOUT_MS);
    const onAbort = () => {
      aborted = true;
      child.kill();
    };
    signal?.addEventListener("abort", onAbort, { once: true });
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      out += chunk;
    });
    child.stderr.on("data", (chunk) => {
      err += chunk;
    });
    child.on("error", (error) => finish(fail, error));
    child.on("close", (code) => finish(settle, { code, out, err, timedOut, aborted }));
  });
}

async function runCli(cliArgs, { cwd, signal, root }) {
  const runPy = locateRunPy(cwd, root);
  const candidates =
    process.env.COOKLINE_PYTHON
      ? [[process.env.COOKLINE_PYTHON, []]]
      : process.platform === "win32"
        ? [
            ["py", ["-3"]],
            ["python", []],
          ]
        : [["python3", []]];
  let lastError;
  for (const [exe, prefix] of candidates) {
    try {
      return await spawnOnce(exe, [...prefix, runPy, ...cliArgs], { cwd, signal });
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
      lastError = error;
    }
  }
  throw new Error(
    `找不到可用的 Python（试过 ${candidates.map(([exe]) => exe).join("、")}）。` +
      `请把 COOKLINE_PYTHON 设为 Python 可执行文件路径。${lastError ? ` 原因：${lastError.message}` : ""}`,
  );
}

function renderRun(result) {
  let text = result.out.replace(/\r\n/g, "\n").trimEnd();
  const err = result.err.replace(/\r\n/g, "\n").trimEnd();
  if (err) text += (text ? "\n" : "") + "[stderr]\n" + err;
  if (result.timedOut) text += `\n[timed out after ${TIMEOUT_MS}ms]`;
  if (result.aborted) text += "\n[aborted]";
  if (result.code !== 0 && result.code !== null) text += `\n[exit code: ${result.code}]`;
  if (!text) text = "(no output)";
  if (text.length > MAX_OUTPUT) {
    text = `${text.slice(0, MAX_OUTPUT)}\n…[truncated; ${text.length - MAX_OUTPUT} chars omitted]`;
  }
  return { text, ok: result.code === 0, exitCode: result.code };
}

function outputSchema() {
  return {
    type: "object",
    properties: {
      text: { type: "string" },
      ok: { type: "boolean" },
      exitCode: { oneOf: [{ type: "integer" }, { type: "null" }] },
    },
    required: ["text", "ok", "exitCode"],
    additionalProperties: false,
  };
}

function desc(recipe = "菜谱卡 JSON 路径（绝对路径，或相对会话工作区）", root = true) {
  return {
    recipe: { type: "string", description: recipe },
    ...(root
      ? {
          root: {
            type: "string",
            description: "可选：方法库根目录（包含 08_作品 的那一层）。默认从会话工作区向上查找。",
          },
        }
      : {}),
  };
}

export function apply(ctx) {
  const cwdOf = async (exec) => {
    try {
      if (ctx.workingDirectory && exec.agent) {
        return await ctx.workingDirectory.ensure(exec.agent, exec.signal);
      }
    } catch {
      // 无法确定会话目录时退回 Host 进程目录；路径错误会在 locateRunPy 中说明。
    }
    return process.cwd();
  };

  const makeTool = (def, command) => ({
    name: def.name,
    description: def.description,
    parameters: def.parameters,
    output: {
      schema: outputSchema(),
      render: (_args, value) => [{ type: "text", text: value.text }],
    },
    timeoutMs: TIMEOUT_MS + 5_000,
    async execute(args, exec) {
      const cwd = await cwdOf(exec);
      const result = await runCli(command(args), { cwd, signal: exec.signal, root: args.root });
      return renderRun(result);
    },
  });

  const tools = [
    makeTool(
      {
        name: "cookline_check",
        description:
          "校验做菜菜谱卡（cookline v2）。默认 strict：WARN 也算不合格。返回 ERROR/WARN/HUMAN 报告；先过这一步再 build。",
        parameters: {
          type: "object",
          properties: {
            ...desc(),
            strict: { type: "boolean", description: "WARN 是否也算不合格，默认 true。" },
          },
          required: ["recipe"],
          additionalProperties: false,
        },
      },
      (args) => ["check", args.recipe, ...(args.strict === false ? [] : ["--strict"])],
    ),
    makeTool(
      {
        name: "cookline_build",
        description:
          "从菜谱卡生成 .monet、runlist、边车与 SRT。不导入、不派发；写文件前会跑 strict 校验。",
        parameters: {
          type: "object",
          properties: {
            ...desc(),
            out: { type: "string", description: "输出 .monet 路径；省略时写在菜谱卡同目录。" },
            force: { type: "boolean", description: "覆盖非 cookline 生成的同名画布。" },
          },
          required: ["recipe"],
          additionalProperties: false,
        },
      },
      (args) => [
        "build",
        args.recipe,
        ...(args.out ? ["-o", args.out] : []),
        ...(args.force ? ["--force"] : []),
      ],
    ),
    makeTool(
      {
        name: "cookline_gate",
        description:
          "分镜闸门：status 看四级签核；approve 签核（必须写看到什么）；runlist 过闸门后只放行节点。approve 只能按 assets→storyboard→keys→videos 顺序。",
        parameters: {
          type: "object",
          properties: {
            ...desc("菜谱卡 JSON 路径（与 build 使用同一份）"),
            action: {
              type: "string",
              enum: ["status", "approve", "runlist"],
              description: "status / approve / runlist。",
            },
            stage: {
              type: "string",
              enum: ["assets", "storyboard", "keys", "videos"],
              description: "approve 与 runlist 必填。",
            },
            note: {
              type: "string",
              description: "approve 必填：这一关实际看到了什么（至少 4 个字）。",
            },
          },
          required: ["recipe", "action"],
          additionalProperties: false,
        },
      },
      (args) => {
        if (args.action === "approve") {
          if (!args.stage || !args.note) throw new Error("approve 需要 stage 和 note");
          return ["gate", "approve", args.recipe, "--stage", args.stage, "--note", args.note];
        }
        if (args.action === "runlist") {
          if (!args.stage) throw new Error("runlist 需要 stage");
          return ["runlist", args.recipe, "--stage", args.stage];
        }
        return ["gate", "status", args.recipe];
      },
    ),
    makeTool(
      {
        name: "cookline_doctor",
        description:
          "审计一张 .monet：接线、提示词字数、负向词、参考图、组重叠、是否手改（prompt digest）。",
        parameters: {
          type: "object",
          properties: {
            canvas: { type: "string", description: ".monet 路径。" },
            recipe: { type: "string", description: "可选：对应菜谱卡，用来对字幕与卡版本。" },
            root: {
              type: "string",
              description: "可选：方法库根目录。默认从会话工作区向上查找。",
            },
          },
          required: ["canvas"],
          additionalProperties: false,
        },
      },
      (args) => ["doctor", args.canvas, ...(args.recipe ? ["--recipe", args.recipe] : [])],
    ),
    makeTool(
      {
        name: "cookline_new",
        description: "按骨架起一张新菜谱卡。写完还要填 areas 与 beats，再 cookline_check。",
        parameters: {
          type: "object",
          properties: {
            series: { type: "string", description: "系列名。" },
            ep: { type: "string", description: "集号，如 EP03。" },
            dish: { type: "string", description: "菜名。" },
            out: { type: "string", description: "输出 JSON 路径。" },
            seriesTitle: { type: "string", description: "可选：系列标题。" },
            character: { type: "string", description: "可选：角色名。" },
            force: { type: "boolean", description: "覆盖同名文件。" },
            root: {
              type: "string",
              description: "可选：方法库根目录。默认从会话工作区向上查找。",
            },
          },
          required: ["series", "ep", "dish"],
          additionalProperties: false,
        },
      },
      (args) => [
        "new",
        "--series",
        args.series,
        "--ep",
        args.ep,
        "--dish",
        args.dish,
        ...(args.out ? ["-o", args.out] : []),
        ...(args.seriesTitle ? ["--series-title", args.seriesTitle] : []),
        ...(args.character ? ["--character", args.character] : []),
        ...(args.force ? ["--force"] : []),
      ],
    ),
    makeTool(
      {
        name: "cookline_migrate",
        description: "把旧菜谱卡迁到 v2 做兼容审计；旧卡补不齐 props/hand/state 时不会直接 build。",
        parameters: {
          type: "object",
          properties: {
            recipe: { type: "string", description: "旧菜谱卡 JSON 路径。" },
            out: { type: "string", description: "迁移后的 v2 JSON 路径。" },
            root: {
              type: "string",
              description: "可选：方法库根目录。默认从会话工作区向上查找。",
            },
          },
          required: ["recipe", "out"],
          additionalProperties: false,
        },
      },
      (args) => ["migrate", args.recipe, "-o", args.out],
    ),
  ];

  for (const tool of tools) {
    ctx.effect(() => ctx.tools.register(tool));
  }
}
