# Detailed Implementation Plan: Project Kickoff & Unified UI

## Phase 1: The Project Kickoff Wizard (New Entry Point)

This component serves as the "Gatekeeper" to the application. It ensures the editor never visualizes an empty state.

### Task 1.1: Create `frontend/src/components/Studio/ProjectWizard.tsx`
*   **Layout:** Full-screen modal overlay (fixed, z-50) with a backdrop blur.
*   **State:**
    *   `videoFiles: File[]`
    *   `audioFile: File | null`
*   **UI Sections:**
    *   **Header:** "Start Your Reel" with a subtitle.
    *   **Main Grid (2 Columns):**
        *   **Left (Audio):** Large Drop zone. Icon toggles to a waveform visualization (fake or real) or file name upon upload. "Requires 1 Master Track".
        *   **Right (Video):** Large Drop zone. Supports multiple files. Displays a grid of thumbnails for uploaded files.
    *   **Footer:** "Enter Studio" button.
        *   *State:* Disabled until `videoFiles.length > 0` AND `audioFile !== null`.
        *   *Action:* Calls a prop `onComplete(videos, audio)` passed from parent.

### Task 1.2: Integrate into `ReelEditor.tsx`
*   **State Change:** Add a state `isProjectInitialized` (boolean).
    *   Default: `false`.
*   **Logic:**
    *   If `!isProjectInitialized`, render `<ProjectWizard />`.
    *   Hide the main editor UI (or render it blurred in background).
*   **Hand-off:**
    *   Define `handleProjectStart(videos, audio)` function.
    *   This function updates the existing `clips` and `music` state using the data from the Wizard.
    *   Sets `isProjectInitialized(true)`.
    *   **Crucial:** This replaces the manual `handleVideoChange` logic for the initial load.

## Phase 2: Refactor Assets Panel (The Unified Library)

Now that the initial files are loaded, the user manages them here.

### Task 2.1: Update `frontend/src/components/Studio/AssetsPanel.tsx`
*   **Props:** Add `audioFile`, `onAudioUpload`, `onAudioDelete` (or similar) to receive the state from `ReelEditor`.
*   **UI Structure:**
    *   Add a **Segmented Control** (Tabs) at the top: `[ Video | Audio ]`.
*   **Tab Logic:**
    *   **Video Tab:** Existing rendering of the video list (draggable cards). Add a compact "Add Clip" button at the bottom or top.
    *   **Audio Tab (New):**
        *   If `audioFile` exists: Show a "Track Card" (Name, Duration, Replace Button, Trash Button).
        *   If `audioFile` is null: Show a "Drop Audio" zone (smaller version of the wizard's drop zone).

### Task 2.2: Pass Props in `ReelEditor.tsx`
*   Connect the `music` state and `setMusic` logic to the new `AssetsPanel` props.

## Phase 3: Timeline Purification

The Timeline is now purely for *manipulating* time, not *importing* files.

### Task 3.1: Clean `frontend/src/components/Studio/TimelinePanel.tsx`
*   **Remove:** The "Plus" (`+`) button in the header.
*   **Refactor Empty State:**
    *   The "Project Wizard" guarantees we enter with files.
    *   However, if a user *deletes* the audio track in the sidebar, the Timeline needs a fallback.
    *   **Change:** Instead of the giant "CLICK TO INGEST" button, show a passive message: *"No Audio Track Selected. Add one in the Library."* or simply a muted placeholder.
*   **Remove:** The `fileInput` ref and upload logic. It is no longer the Timeline's job to handle file I/O.

## Use of Tools
- `read_file` to inspect current prop structures.
- `replace_string_in_file` (or `create_file` for rewrites) to update components.
- `run_in_terminal` to run lints/types checks if needed.
