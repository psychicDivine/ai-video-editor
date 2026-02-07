## Plan: Unified Media Library & Timeline Clean-up

We will resolve the "disjointed" upload UX by consolidating all asset management (Video + Audio) into the Left Sidebar. This aligns with standard NLE (Non-Linear Editor) patterns where the input workflow is unified, leaving the Timeline strictly for editing and visualization.

### Steps
1.  **Refactor `AssetsPanel.tsx`** to include a "Project Assets" segmented control (Videos | Audio).
2.  **Move Audio Ingestion** by adding a "Load Soundtrack" button within the new Audio tab in `AssetsPanel`.
3.  **Update `ReelEditor.tsx`** to pass the audio upload trigger (`musicInputRef`) to `AssetsPanel` instead of `TimelinePanel`.
4.  **Clean `TimelinePanel.tsx`** by removing the "Plus" header button and replacing the "Click to Ingest" empty state with a passive "Drop Audio Here" visual hint.

### Further Considerations
1.  **Direct Drag-and-Drop:** We should ensure users can also drag an audio file directly from their desktop onto the timeline for maximum ease of use.
2.  **Single vs. Multi-Track:** Sticking to the "One Master Track" logic for now, but the new UI will allow swapping the master track easily from the library.

**I will wait for your review of this plan before proceeding.**