"""Save-file management: JSON slots on disk (auto + manual), with metadata."""
import json
import os
import time


class SaveManager:
    SLOTS = ["auto", "1", "2", "3"]

    def __init__(self, base_dir):
        self.dir = os.path.join(base_dir, "saves")
        try:
            os.makedirs(self.dir, exist_ok=True)
        except Exception:
            pass

    def _path(self, slot):
        return os.path.join(self.dir, "slot_%s.json" % slot)

    def save(self, slot, state):
        data = dict(state)
        data["saved_at"] = time.time()
        try:
            with open(self._path(slot), "w") as f:
                json.dump(data, f, indent=1)
            return True
        except Exception:
            return False

    def load(self, slot):
        try:
            with open(self._path(slot)) as f:
                return json.load(f)
        except Exception:
            return None

    def list(self):
        return {slot: self.load(slot) for slot in self.SLOTS}

    def latest(self):
        best, bt = None, -1.0
        for slot in self.SLOTS:
            m = self.load(slot)
            if m and m.get("saved_at", 0) > bt:
                bt = m["saved_at"]
                best = slot
        return best

    def has_any(self):
        return self.latest() is not None

    @staticmethod
    def describe(state):
        """Short human label for a save in the slot menu."""
        if not state:
            return "— empty —"
        act = state.get("act", 1)
        loc = state.get("location", state.get("scene", "?"))
        pt = int(state.get("playtime", 0))
        mm, ss = pt // 60, pt % 60
        when = ""
        if state.get("saved_at"):
            try:
                when = time.strftime("%b %d  %H:%M", time.localtime(state["saved_at"]))
            except Exception:
                when = ""
        return "Act %d  -  %s    %d:%02d    %s" % (act, loc, mm, ss, when)
