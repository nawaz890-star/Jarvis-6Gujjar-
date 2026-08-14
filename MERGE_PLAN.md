# Branch Merge Plan

## Overview
Combining all 10 phase branches into main following this sequence to resolve dependencies:

1. **phase1-scaffold** → main (Foundation: config, logging, core app, memory structure)
2. **phase2-ai** → main (AI providers: Gemini, Ollama, fallback, chat manager)
3. **phase3-voice** → main (Voice: microphone, STT, TTS, wake-word detection)
4. **phase4-memory** → main (Enhanced memory: long-term memory manager)
5. **phase5-automation** → main (Automation: file/app/system operations)
6. **phase6-web** → main (Web: search, weather, news, caching)
7. **phase7-gui** → main (GUI: PySide6 main window, UI controller)
8. **phase8-vision** → main (Vision: camera, OCR capabilities)
9. **phase9-plugins** → main (Plugin system: manager, runner, sample plugin)
10. **phase10-testing-packaging** → main (Testing and packaging)

## Merge Strategy
- Sequential merges to avoid conflicts
- All changes combined into main branch
- Feature branches remain for history
