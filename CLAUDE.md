# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HAGIA is a creative studio portfolio website featuring an immersive 3D experience built with Three.js. The site showcases video work through an interactive scroll-driven 3D environment with a geodesic dome, terrain, billboards, and work panels.

## Development Commands

**Start local server with video streaming support:**
```bash
python3 serve.py
```
Server runs at http://localhost:8000. The custom server handles HTTP Range requests for proper video streaming and CORS headers.

## Architecture

### Single-Page Application
- `index.html` - The entire application in one file (~5000+ lines), containing:
  - CSS styles (lines 1-407)
  - HTML structure (lines 408-444)
  - JavaScript/Three.js application (lines 445+)

### Key Three.js Components
- **Scene elements**: Geodesic dome, procedural terrain with Simplex noise, star field, horizon glow
- **Billboards**: 6 floating panels around the dome, each loading 3D logo models (.obj/.fbx files)
- **Works section**: 11 video-based work panels displayed as floating cards
- **Totem scene**: Separate Three.js overlay for the HAGIA logo

### Data Structure
`WORKS_DATA` array (lines 454-543) defines all portfolio items with:
- `id`, `title`, `folder` (path in videos directory)
- `videos` array (video filenames)
- `descFile` (optional .txt file with metadata)
- `description` (fallback text)

### Video Content Structure
```
videos/
├── [PROJECT NAME]/
│   ├── [PROJECT NAME].txt  (optional metadata)
│   └── video1.mp4, video2.mp4...
```
Text files contain metadata (KEY: Value pairs) followed by "Overview" section.

### Key Functions
- `init()` - Main initialization, creates all 3D objects
- `animate()` - Main render loop with scroll-based animations
- `createWorksSection()` - Builds the floating work panels
- `openWorkDetail(workIndex)` / `closeWorkDetail()` - Work detail page management
- `onScroll()` - Handles scroll-driven camera movement and reveal effects

### External Dependencies (CDN)
- Three.js r128
- OBJLoader, FBXLoader, RGBELoader (Three.js examples)
- fflate (compression for FBX)
- Space Grotesk font (Google Fonts)

### Asset Files
- `hagia_logo.png` - Main logo
- `logo_0.obj` through `logo_4.obj`, `logo_5.fbx` - 3D billboard logos
- `higia_logo.obj` - 3D logo model
