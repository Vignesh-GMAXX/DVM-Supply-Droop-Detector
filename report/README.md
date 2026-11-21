# Report

- **[P1G11_FinalReport.pdf](P1G11_FinalReport.pdf)**: the submitted final report (IEEE format, 11 pages: main text to page 9, appendices A1–A6 and B after it).
- **[latex/](latex)**: its source. Upload the folder to Overleaf (or compile locally with the IEEEtran class installed):

  ```bash
  cd latex
  pdflatex main && bibtex main && pdflatex main && pdflatex main
  ```

  `fig_*.pdf` are the data figures (regenerate with `scripts/reproduce_figures.sh`), `fig_hierarchy.pdf` comes from `diagrams/`, and `img_*.png` / `extra_images/` are Virtuoso layout and schematic screenshots.
