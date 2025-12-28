import { createApp, h } from 'vue';
import { SlidesRender } from 'slidev-parser';
import 'slidev-parser/index.css';
import yaml from 'js-yaml';

export interface PreviewState {
  app: ReturnType<typeof createApp> | null;
}

export function createPreviewState(): PreviewState {
  return {
    app: null,
  };
}

export function cleanupPreview(state: PreviewState, mountEl: HTMLElement | null): void {
  if (state.app) {
    state.app.unmount();
    state.app = null;
  }
  if (mountEl) {
    mountEl.innerHTML = '';
  }
}

interface Slide {
  frontmatter: Record<string, any>;
  content: string;
}

// Basic Slidev Markdown Parser
function parseSlidevMarkdown(markdown: string): Slide[] {
  const lines = markdown.split(/\r?\n/);
  const slides: Slide[] = [];
  let currentContent: string[] = [];
  let currentFrontmatter: string[] = [];
  let inFrontmatter = false;
  let isFirstLine = true;

  const flushSlide = () => {
    if (currentContent.length > 0 || currentFrontmatter.length > 0) {
      let fm = {};
      try {
        if (currentFrontmatter.length > 0) {
            fm = yaml.load(currentFrontmatter.join('\n')) as Record<string, any> || {};
        }
      } catch (e) {
        console.error('Failed to parse frontmatter', e);
      }

      slides.push({
        frontmatter: fm,
        content: currentContent.join('\n')
      });
    }
    currentContent = [];
    currentFrontmatter = [];
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isSeparator = line.trim() === '---';

    if (isSeparator) {
      if (isFirstLine) {
        // Start of file frontmatter
        inFrontmatter = true;
        isFirstLine = false;
        continue;
      }
      
      if (inFrontmatter) {
        // End of frontmatter
        inFrontmatter = false;
        continue;
      }

      // Slide separator
      flushSlide();
      // Check if next lines look like frontmatter
      // In Slidev, --- separates slides. The next slide might start with frontmatter block?
      // Slidev syntax usually:
      // ---
      // layout: cover
      // ---
      // # Title
      //
      // If we see ---, we flush previous slide.
      // The NEW slide starts. If it immediately has frontmatter key-values?
      // Actually Slidev treats content between --- and --- as frontmatter if it parses as valid YAML.
      // But here we see --- as separator.
      
      // Let's assume standard Slidev format:
      // Slide 1
      // ---
      // layout: center
      // ---
      // Slide 2
      
      // If we hit ---, we flush.
      // Then we look ahead. If the NEXT block is followed by another ---, it is frontmatter.
      
      // Implementation simplification:
      // Treat --- as a delimiter.
      // If we are NOT in frontmatter, --- starts a new context.
      // If the subsequent content is valid YAML and followed by ---, it is frontmatter.
      // This is hard to do line-by-line.
      
      // Let's switch to regex based splitting for robustness with Slidev syntax
      // Regex for slide separator: ^---$ (multiline)
      continue; 
    }
    
    if (inFrontmatter) {
        currentFrontmatter.push(line);
    } else {
        currentContent.push(line);
    }
    isFirstLine = false;
  }
  
  flushSlide();
  
  // Post-processing to handle "frontmatter-only" slides which are actually frontmatter for the *next* slide?
  // No, let's use a simpler regex splitter which is more reliable for Slidev
  return parseSlidevRegex(markdown);
}

function parseSlidevRegex(markdown: string): Slide[] {
    // 1. Split by --- separator
    // But be careful about code blocks.
    // Ideally we'd use a robust parser, but here is a "good enough" regex.
    const slides: Slide[] = [];
    
    // Normalize newlines
    const normalized = markdown.replace(/\r\n/g, '\n');
    
    // Split by ^---$
    // Note: This doesn't handle --- inside code blocks.
    // Assuming generated content is well-behaved.
    const parts = normalized.split(/(?:^|\n)---\n/);

    // The first part is the first slide (or frontmatter of first slide).
    // In Slidev:
    // ---
    // layout: cover
    // ---
    // Title
    
    // Part 0: empty (if file starts with ---)
    // Part 1: layout: cover
    // Part 2: Title
    
    // If file DOES NOT start with ---
    // Title
    // ---
    // layout: center
    // ---
    // Content
    
    // Part 0: Title
    // Part 1: layout: center
    // Part 2: Content
    
    let currentSlide: Slide = { frontmatter: {}, content: '' };
    
    for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (!part.trim()) continue; // Skip empty parts (like before first ---)
        
        // Try to parse as YAML
        let isYaml = false;
        let parsedYaml = {};
        try {
            parsedYaml = yaml.load(part) as any;
            if (typeof parsedYaml === 'object' && parsedYaml !== null) {
                isYaml = true;
            }
        } catch (e) {
            // Not yaml
        }

        if (isYaml && i < parts.length - 1 && parts[i+1]) {
            // If this part is YAML and there is a next part, 
            // treat this as frontmatter for the NEXT part (or current slide context)
            // Wait, logic is:
            // [Content] --- [Frontmatter] --- [Content]
            // We should attach Frontmatter to the FOLLOWING content?
            // Slidev logic:
            // Separator is `---`.
            // If a block is valid YAML (and maybe implicitly if it's between two `---`), it's frontmatter.
            
            // Let's assume the previous slide is done.
            // We are starting a new slide.
            // If this part is YAML, it's the frontmatter for the new slide.
            currentSlide = { frontmatter: parsedYaml, content: '' };
            
            // But what if it's just content that looks like YAML?
            // Slidev requires frontmatter to be wrapped in `---` if it's not at the very beginning of the file?
            // Actually, `---` IS the wrapper.
            
            // Case A:
            // ---
            // layout: a
            // ---
            // Content A
            // ---
            // layout: b
            // ---
            // Content B
            
            // Split: "", "layout: a", "Content A", "layout: b", "Content B"
            // i=1 is yaml. Set currentSlide.fm = ...
            // i=2 is content. Set currentSlide.content = ... -> Push
            
            // Case B:
            // Content A
            // ---
            // Content B
            
            // Split: "Content A", "Content B"
            // i=0 not yaml. Content A -> Push
            // i=1 not yaml. Content B -> Push
            
            if (currentSlide.content) {
                // If we already have content, push it as a slide (with empty frontmatter if none set)
                // BUT, in Case A, i=2 "Content A". currentSlide has fm from i=1.
                // We set content and Push.
            }
            
        } else {
             // Treat as content
             currentSlide.content = part;
             slides.push(currentSlide);
             currentSlide = { frontmatter: {}, content: '' };
        }
    }
    
    // Refined logic loop:
    const resultSlides: Slide[] = [];
    let pendingFrontmatter: any = {};
    
    parts.forEach((part, index) => {
        // Heuristic: If part is valid YAML and short-ish, treat as frontmatter
        // This is risky. 
        // Let's use a simpler approach: 
        // If file starts with ---, then odd parts are frontmatter, even parts are content.
        // If file does NOT start with ---, even parts are content, odd parts are frontmatter?
        
        // Let's stick to the simplest interpretation:
        // Render everything as content for now, if parsing fails.
        // But we need layout support.
        
        // Let's try to parse ONLY if it looks like frontmatter (has key: value structure)
        if (part.includes(':')) {
             try {
                const doc = yaml.load(part);
                if (doc && typeof doc === 'object') {
                    pendingFrontmatter = doc;
                    return;
                }
             } catch {}
        }
        
        resultSlides.push({
            frontmatter: pendingFrontmatter,
            content: part
        });
        pendingFrontmatter = {};
    });

    return resultSlides;
}


export async function renderVueComponent(
  code: string,
  containerEl: HTMLElement,
  mountEl: HTMLElement,
  state: PreviewState
): Promise<void> {
  // Cleanup previous state
  cleanupPreview(state, mountEl);

  if (!code.trim()) {
    throw new Error('No content provided.');
  }

  // Parse Markdown to Slides
  // We use the simpler regex parser from above, slightly improved
  const slides = parseSlidevRegex(code);

  state.app = createApp({
    setup() {
      return () => h(SlidesRender, {
        slides: slides,
        // Optional: style configs
      });
    }
  });

  state.app.mount(mountEl);
}