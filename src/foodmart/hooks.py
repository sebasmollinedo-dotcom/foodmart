"""Hooks del proyecto."""
import logging
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

from kedro.framework.hooks import hook_impl

logger = logging.getLogger(__name__)


class OpenReportHook:
    """Abre el reporte HTML en Google Chrome cuando ``kedro run`` lo acaba de generar."""

    @hook_impl
    def after_pipeline_run(self, run_params: dict, pipeline) -> None:
        """Abre el reporte, salvo en CI, con ``KEDRO_OPEN_REPORT=0`` o si no se regeneró.

        Un fallo al abrir el navegador nunca debe hacer fallar la corrida.
        """
        if os.environ.get("CI") or os.environ.get("KEDRO_OPEN_REPORT") == "0":
            return
        if "build_report" not in {node.name for node in pipeline.nodes}:
            return  # p. ej. `kedro run --pipeline data_processing`: no hay reporte nuevo
        report = Path(run_params["project_path"]) / "data" / "08_reporting" / "reporte.html"
        if not report.exists():
            return
        try:
            if sys.platform == "darwin":
                cmd = ["open", "-a", "Google Chrome", str(report)]
                if subprocess.run(cmd, capture_output=True).returncode != 0:
                    subprocess.run(["open", str(report)], capture_output=True)
            else:
                webbrowser.open(report.as_uri())
        except Exception as error:  # noqa: BLE001
            logger.warning("No se pudo abrir el reporte (%s): %s", report, error)
