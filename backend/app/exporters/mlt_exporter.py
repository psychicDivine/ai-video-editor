"""Simple MLT exporter for Shotcut/Kdenlive compatibility.

This exporter writes a minimal MLT XML project containing producers
for each clip and a playlist. It also emits commented transition hints
so users can open the XML in an editor and add/adjust transitions.

Note: This is a pragmatic, minimal exporter intended for manual tuning
in OSS editors rather than a full-featured MLT generator.
"""

from pathlib import Path
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


class MLTExporter:
    """Export a list of clips and optional transition hints to an MLT XML file."""

    def __init__(self, profile: Optional[Dict] = None):
        # Default vertical mobile profile
        self.profile = profile or {
            "width": "1080",
            "height": "1920",
            "frame_rate_num": "30",
            "frame_rate_den": "1",
            "progressive": "1",
        }

    def export(self, clips: List[Dict], output_path: str, title: str = "project") -> str:
        """
        clips: list of dicts {"path": "/abs/path/to/file.mp4", "in": 0, "out": None, "transition": {"type":"dissolve","duration":1.0}}

        Returns path to written MLT file.
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        mlt = ET.Element("mlt")
        mlt.set("LC_NUMERIC", "C")

        profile = ET.SubElement(mlt, "profile")
        for k, v in self.profile.items():
            profile.set(k, str(v))

        # Producers
        producers = []
        for i, clip in enumerate(clips):
            pid = f"producer{i}"
            p = ET.SubElement(mlt, "producer", id=pid)
            ET.SubElement(p, "property", name="resource").text = str(Path(clip["path"]).as_posix())
            producers.append(pid)

        # Playlist
        playlist = ET.SubElement(mlt, "playlist", id="playlist0")
        for i, pid in enumerate(producers):
            entry_attrs = {}
            if clips[i].get("in") is not None:
                entry_attrs["in"] = str(int(clips[i].get("in", 0)))
            if clips[i].get("out") is not None:
                entry_attrs["out"] = str(int(clips[i].get("out")))
            ET.SubElement(playlist, "entry", producer=pid, **entry_attrs)

        # Tractor/playlist wrapper
        tractor = ET.SubElement(mlt, "tractor")
        multitrack = ET.SubElement(tractor, "multitrack")
        ET.SubElement(multitrack, "track", producer="playlist0")

        # Add human-readable transition hints as XML comments.
        # MLT transitions are complex across editors; keep hints to guide manual edits.
        comments = []
        for i in range(len(clips) - 1):
            t = clips[i].get("transition") or {}
            ttype = t.get("type", "dissolve")
            td = t.get("duration", 1.0)
            comments.append(f"Transition between producer{i} and producer{i+1}: {ttype} duration={td}s")

        for c in comments:
            mlt.append(ET.Comment(c))

        tree = ET.ElementTree(mlt)
        tree.write(out, encoding="utf-8", xml_declaration=True)

        logger.info(f"MLT project exported to {out}")
        return str(out)
