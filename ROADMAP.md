# Music-Reactive Kaleidoscope Visualizer -- Roadmap

## Current State
A feature-rich real-time audio visualization app with PyQt5 rendering, PyAudio input, particle systems, multiple symmetry modes, 3D effects, beat detection, and a plugin architecture. Well-modularized: `src/core/` (kaleidoscope_engine.py 658 lines, audio_processing.py, visualization_components.py, particle_effects.py), `src/ui/` (control_panel.py 1831 lines, widgets.py, debug_console.py), `src/app/` (main_window.py), `src/plugins/` (plugins.py), and `src/experimental/` (audio_ml.py, liquid_physics.py, organic_growth.py, reality_distortion.py, dimensional_transitions.py). A `standalone/` directory has older monolithic versions. The `control_panel.py` at 1831 lines is extremely oversized.

## Short-term Improvements
- [ ] Split `control_panel.py` (1831 lines) into `visual_controls.py`, `audio_controls.py`, `effect_controls.py`, `wireframe_controls.py` -- one file per tab/section
- [ ] Remove or archive `standalone/kaleidoscope_OLD.py` -- it is clearly superseded
- [ ] Add type hints to `kaleidoscope_engine.py` and `visualization_components.py`
- [ ] Add docstrings to the experimental modules (they lack documentation)
- [ ] Create unit tests for audio processing (FFT, beat detection) and color generation
- [ ] Add a `requirements.txt` if not present (PyQt5, PyAudio, numpy)
- [ ] Document the experimental features and how to enable them

## Feature Enhancements
- [ ] Add audio file input mode (play MP3/WAV) in addition to microphone capture
- [ ] Implement preset system -- save/load visualization configurations to JSON
- [ ] Add MIDI controller support for hands-free parameter control during performances
- [ ] Implement screen recording/export to video (MP4/GIF)
- [ ] Add more symmetry modes: hexagonal, pentagonal, fractal
- [ ] Implement transition effects between symmetry modes and color schemes
- [ ] Add BPM display and tempo-synced effects in the UI
- [ ] Expose the experimental effects (liquid physics, organic growth, dimensional transitions) in the main UI

## Long-term Vision
- [ ] Migrate rendering to OpenGL/Vulkan for significantly better performance
- [ ] Add Spotify/system audio integration for visualizing any playing audio
- [ ] Implement a visual scripting system for creating custom effect chains
- [ ] Add VJ/performance mode with cue lists and crossfading
- [ ] Create a Syphon/Spout output for integration with projection mapping software
- [ ] Package as a standalone app for non-technical users

## Technical Debt
- [ ] `control_panel.py` at 1831 lines is the most urgent file to split
- [ ] `src/experimental/` has 5 modules but no clear integration path to the main app
- [ ] `standalone/` directory should be archived or removed
- [ ] The plugin system in `src/plugins/plugins.py` should be expanded to match the experimental features pattern
- [ ] Audio processing at 107 lines seems thin -- verify FFT windowing and smoothing are robust
- [ ] No performance profiling -- identify bottleneck between rendering and audio processing
