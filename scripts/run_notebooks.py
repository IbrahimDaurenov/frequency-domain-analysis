"""Execute selected notebooks with this Python, preserving all outputs."""
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

for path in (list(map(Path, sys.argv[1:])) or sorted(Path("notebooks").glob("*.ipynb"))):
    notebook = nbformat.read(path, as_version=4)
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    try:
        NotebookClient(notebook, timeout=180, km=manager,
                       resources={"metadata": {"path": str(Path.cwd())}}).execute()
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
        manager.cleanup_resources()
    nbformat.write(notebook, path)
    print(f"Executed {path}", flush=True)
