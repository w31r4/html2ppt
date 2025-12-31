"""Inject adaptive fit-scale helper into Vue SFC components."""

from __future__ import annotations

import re

FIT_SCALE_HELPER_MARKER = "fit-scale-helper"

_SCRIPT_SETUP_RE = re.compile(
    r"(<script\s+setup[^>]*>)([\s\S]*?)(</script>)",
    re.IGNORECASE,
)
_TEMPLATE_CLOSE_RE = re.compile(r"</template>", re.IGNORECASE)
_VUE_IMPORT_RE = re.compile(
    r"import\s*{([^}]*)}\s*from\s*['\"]vue['\"]\s*;?",
    re.IGNORECASE,
)

_FIT_SCALE_HELPER_BODY = """// fit-scale-helper
const fitScaleInstance = getCurrentInstance();
let fitScaleFrame = null;
let fitScaleResizeObserver = null;
let fitScaleMutationObserver = null;
let fitScaleValue = 1;

const fitScaleSupportsScale =
  typeof CSS !== 'undefined' &&
  typeof CSS.supports === 'function' &&
  CSS.supports('scale', '1');
const fitScaleSupportsZoom =
  !fitScaleSupportsScale &&
  typeof CSS !== 'undefined' &&
  typeof CSS.supports === 'function' &&
  CSS.supports('zoom', '1');

const fitScaleApply = () => {
  const rootEl = fitScaleInstance?.proxy?.$el;
  if (!(rootEl instanceof HTMLElement)) return;

  const width = rootEl.clientWidth;
  const height = rootEl.clientHeight;
  let scrollWidth = rootEl.scrollWidth;
  let scrollHeight = rootEl.scrollHeight;

  if (fitScaleSupportsZoom && fitScaleValue) {
    scrollWidth /= fitScaleValue;
    scrollHeight /= fitScaleValue;
  }

  if (!width || !height || !scrollWidth || !scrollHeight) return;

  const nextScale = Math.min(1, width / scrollWidth, height / scrollHeight);
  fitScaleValue = nextScale;

  if (fitScaleSupportsScale) {
    rootEl.style.scale = `${nextScale}`;
  } else if (fitScaleSupportsZoom) {
    rootEl.style.zoom = `${nextScale}`;
  } else {
    rootEl.style.transform = `scale(${nextScale})`;
    rootEl.style.transformOrigin = 'top left';
  }
};

const fitScaleSchedule = () => {
  if (fitScaleFrame !== null) {
    cancelAnimationFrame(fitScaleFrame);
  }
  fitScaleFrame = requestAnimationFrame(() => {
    fitScaleFrame = null;
    fitScaleApply();
  });
};

onMounted(() => {
  nextTick(() => {
    const rootEl = fitScaleInstance?.proxy?.$el;
    if (!(rootEl instanceof HTMLElement)) return;

    fitScaleResizeObserver = new ResizeObserver(() => fitScaleSchedule());
    fitScaleResizeObserver.observe(rootEl);

    fitScaleMutationObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (
          mutation.type === 'attributes' &&
          mutation.target === rootEl &&
          mutation.attributeName === 'style'
        ) {
          continue;
        }
        fitScaleSchedule();
        break;
      }
    });
    fitScaleMutationObserver.observe(rootEl, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['class', 'style'],
    });

    if (document.fonts?.ready) {
      document.fonts.ready.then(() => fitScaleSchedule()).catch(() => {});
    }

    fitScaleSchedule();
  });
});

onBeforeUnmount(() => {
  fitScaleResizeObserver?.disconnect();
  fitScaleMutationObserver?.disconnect();
  if (fitScaleFrame !== null) {
    cancelAnimationFrame(fitScaleFrame);
  }
});
"""

_FIT_SCALE_IMPORTS = ["getCurrentInstance", "nextTick", "onBeforeUnmount", "onMounted"]


def _collect_vue_imports(script_content: str) -> set[str]:
    imports: set[str] = set()
    for match in _VUE_IMPORT_RE.finditer(script_content):
        raw = match.group(1)
        for part in raw.split(","):
            name = part.strip()
            if not name:
                continue
            if " as " in name:
                name = name.split(" as ", 1)[0].strip()
            imports.add(name)
    return imports


def _inject_into_script_setup(content: str) -> str:
    if FIT_SCALE_HELPER_MARKER in content:
        return content

    existing_imports = _collect_vue_imports(content)
    missing = [name for name in _FIT_SCALE_IMPORTS if name not in existing_imports]

    import_block = ""
    if missing:
        import_list = ", ".join(missing)
        import_block = f"import {{ {import_list} }} from 'vue';\n"

    updated = content.strip()
    if import_block:
        updated = import_block + updated

    if updated:
        updated += "\n\n" + _FIT_SCALE_HELPER_BODY
    else:
        updated = _FIT_SCALE_HELPER_BODY

    return updated + "\n"


def _append_script_setup(code: str) -> str:
    helper_block = "<script setup>\n"
    helper_block += f"import {{ {', '.join(_FIT_SCALE_IMPORTS)} }} from 'vue';\n\n"
    helper_block += _FIT_SCALE_HELPER_BODY
    helper_block += "\n</script>\n"

    match = _TEMPLATE_CLOSE_RE.search(code)
    if not match:
        return code.rstrip() + "\n\n" + helper_block

    insert_at = match.end()
    return code[:insert_at] + "\n\n" + helper_block + code[insert_at:]


def inject_fit_scale_helper(code: str) -> str:
    """Ensure Vue SFC includes fit-scale helper logic."""
    if FIT_SCALE_HELPER_MARKER in code:
        return code

    match = _SCRIPT_SETUP_RE.search(code)
    if match:
        open_tag, content, close_tag = match.groups()
        updated_content = _inject_into_script_setup(content)
        return code[: match.start()] + open_tag + updated_content + close_tag + code[match.end() :]

    return _append_script_setup(code)
