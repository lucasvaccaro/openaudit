import sys
import logging as log
import snapshot

log.basicConfig(stream=sys.stdout, level=log.INFO)

snap = snapshot.Snapshot()
id = snap.create()

log.info("Created snapshot id %s", id)