"""Generate PDF report for MSDC-2-4-CUS4-005 camera initial evaluation."""

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
from datetime import date

DATA_DIR = "data"
OUT_PDF  = "MSDC_Camera_Evaluation_Report.pdf"

# ── Load all images ──────────────────────────────────────────────────────────
with rasterio.open(f"{DATA_DIR}/frame_000362-RGB.tif")       as s: rgb   = s.read()
with rasterio.open(f"{DATA_DIR}/frame_000362-bio.tif")       as s: bio   = s.read()
with rasterio.open(f"{DATA_DIR}/frame_000362-swir-1125.tif") as s: s1125 = s.read(1)
with rasterio.open(f"{DATA_DIR}/frame_000362-swir-1275.tif") as s: s1275 = s.read(1)

# ── Band metadata ────────────────────────────────────────────────────────────
RGB_BANDS  = [("Green",540,60,"green"),("Blue",470,60,"steelblue"),
              ("Red",630,60,"red"),("Green2",540,60,"darkgreen")]
BIO_BANDS  = [("NIR1",735,25,"darkblue"),("NIR2",800,25,"purple"),
              ("NIR3",865,25,"darkorange"),("NIR4",930,25,"brown")]

# ── ROIs ─────────────────────────────────────────────────────────────────────
RGB_ROIS  = {"White":{"rows":(495,520),"cols":(750,775),"color":"blue"},
             "Black":{"rows":(695,710),"cols":(610,625),"color":"red"}}
BIO_ROIS  = {"White":{"rows":(245,255),"cols":(310,320),"color":"blue"},
             "Black":{"rows":(342,352),"cols":(235,245),"color":"red"}}
S1125_ROIS= {"White":{"rows":(480,490),"cols":(765,775),"color":"blue"},
             "Black":{"rows":(700,710),"cols":(600,610),"color":"red"}}
S1275_ROIS= {"White":{"rows":(480,490),"cols":(695,705),"color":"blue"},
             "Black":{"rows":(700,710),"cols":(520,530),"color":"red"}}

def pct_stretch(arr, lo=2, hi=98):
    p0, p1 = np.percentile(arr, lo), np.percentile(arr, hi)
    return np.clip((arr.astype(float)-p0)/(p1-p0), 0, 1)

def roi_stats(arr, roi):
    r0,r1 = roi["rows"]; c0,c1 = roi["cols"]
    patch = arr[r0:r1, c0:c1]
    return dict(min=int(patch.min()), max=int(patch.max()),
                mean=float(patch.mean()), median=float(np.median(patch)),
                std=float(patch.std()))

def assess(wht_med, max_dn, blk_med):
    contrast  = wht_med/blk_med if blk_med>0 else float("inf")
    pct       = wht_med/max_dn*100
    if wht_med >= max_dn*0.99: status = "SATURATED"
    elif wht_med < max_dn*0.05: status = "WEAK"
    elif contrast < 5:          status = "LOW CONTRAST"
    else:                       status = "OK"
    return contrast, pct, status

COLORS = {"OK":"#2ecc71","SATURATED":"#e74c3c","WEAK":"#e67e22","LOW CONTRAST":"#f39c12"}

with PdfPages(OUT_PDF) as pdf:

    # ── Page 1: Title ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor("#1a1a2e")
    ax = fig.add_axes([0,0,1,1]); ax.axis("off")
    ax.text(0.5, 0.72, "MSDC-2-4-CUS4-005", ha="center", va="center",
            fontsize=32, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.60, "Multispectral Camera — Initial Evaluation Report",
            ha="center", va="center", fontsize=18, color="#a0c4ff", transform=ax.transAxes)
    ax.text(0.5, 0.50, "Spectral Devices Inc.", ha="center", va="center",
            fontsize=14, color="#cccccc", transform=ax.transAxes)
    ax.text(0.5, 0.38, f"Frame: 000362  |  Date: {date.today().strftime('%d %B %Y')}",
            ha="center", va="center", fontsize=12, color="#aaaaaa", transform=ax.transAxes)
    # Camera specs table
    specs = [["Camera","Model","Bands","Bit Depth","Sensor"],
             ["RGB","MSC2-RGB-1-A","4 (G/B/R/G2)","12-bit","1024×1024"],
             ["BIO","MSC2-BIO-1-A","4 (NIR1–4)","12-bit","512×512"],
             ["SWIR 1125","—","1","~15-bit","1024×1280"],
             ["SWIR 1275","—","1","~15-bit","1024×1280"]]
    tbl = ax.table(cellText=specs[1:], colLabels=specs[0],
                   loc="center", bbox=[0.1, 0.06, 0.8, 0.26])
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for (r,c), cell in tbl.get_celld().items():
        cell.set_facecolor("#16213e" if r==0 else "#0f3460")
        cell.set_text_props(color="white")
        cell.set_edgecolor("#a0c4ff")
    pdf.savefig(fig, dpi=150); plt.close()

    # ── Page 2: Band wavelength overview ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.suptitle("Band Wavelength Overview", fontsize=16, fontweight="bold", y=0.97)
    all_bands = [(n,c,fw,col,"RGB") for n,c,fw,col in RGB_BANDS] + \
                [(n,c,fw,col,"BIO") for n,c,fw,col in BIO_BANDS] + \
                [("SWIR",1125,30,"teal","SWIR"),("SWIR",1275,30,"darkorchid","SWIR")]
    for name,cwl,fwhm,color,cam in all_bands:
        ax.barh(cam, fwhm, left=cwl-fwhm/2, height=0.4, color=color, alpha=0.7, edgecolor="black")
        ax.text(cwl, cam, f"{cwl}nm", ha="center", va="center", fontsize=8, fontweight="bold")
    ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.set_xlim(400, 1400)
    ax.grid(axis="x", alpha=0.3)
    ax.set_title("Each bar = FWHM bandwidth centred on CWL", fontsize=10, color="gray")
    pdf.savefig(fig, dpi=150); plt.close()

    # ── Page 3: RGB — composite + histograms ─────────────────────────────────
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle("RGB Camera — frame_000362", fontsize=14, fontweight="bold")
    gs = GridSpec(2, 4, figure=fig, hspace=0.4, wspace=0.35)

    # composite
    R = pct_stretch(rgb[2]); G = pct_stretch(rgb[0]); B = pct_stretch(rgb[1])
    comp = np.stack([R,G,B], axis=-1)
    ax_comp = fig.add_subplot(gs[0, :2])
    ax_comp.imshow(comp); ax_comp.set_title("True colour composite\n(R:630 G:540 B:470 nm)", fontsize=9)
    ax_comp.axis("off")
    for label, roi in RGB_ROIS.items():
        r0,r1=roi["rows"]; c0,c1=roi["cols"]
        ax_comp.add_patch(patches.Rectangle((c0,r0),c1-c0,r1-r0,
            linewidth=2,edgecolor=roi["color"],facecolor="none"))
        ax_comp.text(c0,r0-8,label,color=roi["color"],fontsize=7,fontweight="bold")

    # individual bands
    for idx,(name,cwl,_,color) in enumerate(RGB_BANDS):
        ax = fig.add_subplot(gs[0, 2] if idx<2 else gs[0, 3])
        # stack 2 per subplot
        if idx % 2 == 0:
            ax_b = fig.add_subplot(gs[0, 2+idx//2])
        ax_b.imshow(pct_stretch(rgb[idx]), cmap="gray")
        ax_b.set_title(f"{name}\n{cwl}nm", fontsize=8); ax_b.axis("off")

    # histograms
    for idx,(name,cwl,_,color) in enumerate(RGB_BANDS):
        ax = fig.add_subplot(gs[1, idx])
        ch = rgb[idx].ravel()
        ax.hist(ch, bins=128, color=color, alpha=0.8, log=True)
        ax.axvline(np.median(ch), color="black", linestyle="--", linewidth=1)
        wmed = roi_stats(rgb[idx], RGB_ROIS["White"])["median"]
        bmed = roi_stats(rgb[idx], RGB_ROIS["Black"])["median"]
        ax.axvline(wmed, color="blue",  linestyle=":", linewidth=1.5, label=f"W={wmed:.0f}")
        ax.axvline(bmed, color="red",   linestyle=":", linewidth=1.5, label=f"B={bmed:.0f}")
        ax.set_title(f"{name} {cwl}nm", fontsize=8)
        ax.set_xlabel("DN", fontsize=7); ax.legend(fontsize=6)
        ax.tick_params(labelsize=6)
    pdf.savefig(fig, dpi=150); plt.close()

    # ── Page 4: BIO histograms ────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    fig.suptitle("BIO Camera (NIR) — frame_000362", fontsize=14, fontweight="bold")
    for ax,(name,cwl,_,color) in zip(axes.flat, BIO_BANDS):
        ch = bio[BIO_BANDS.index((name,cwl,_,color))].ravel()
        ax.hist(ch, bins=128, color=color, alpha=0.8, log=True)
        idx = BIO_BANDS.index((name,cwl,_,color))
        wmed = roi_stats(bio[idx], BIO_ROIS["White"])["median"]
        bmed = roi_stats(bio[idx], BIO_ROIS["Black"])["median"]
        ax.axvline(wmed, color="blue", linestyle=":", linewidth=1.5, label=f"White={wmed:.0f}")
        ax.axvline(bmed, color="red",  linestyle=":", linewidth=1.5, label=f"Black={bmed:.0f}")
        ax.set_title(f"{name} — {cwl} nm", fontsize=11)
        ax.set_xlabel("DN (0–4095)"); ax.legend(fontsize=9)
    plt.tight_layout()
    pdf.savefig(fig, dpi=150); plt.close()

    # ── Page 5: SWIR images ───────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    fig.suptitle("SWIR Cameras — frame_000362", fontsize=14, fontweight="bold")
    for ax, arr, rois, title in [
        (axes[0,0], s1125, S1125_ROIS, "SWIR 1125 nm — percentile stretch"),
        (axes[0,1], s1275, S1275_ROIS, "SWIR 1275 nm — percentile stretch"),
        (axes[1,0], s1125, S1125_ROIS, "SWIR 1125 nm — histogram"),
        (axes[1,1], s1275, S1275_ROIS, "SWIR 1275 nm — histogram"),
    ]:
        if "histogram" in title:
            ax.hist(arr.ravel(), bins=128, color="teal" if "1125" in title else "darkorchid",
                    alpha=0.8, log=True)
            for label,roi in rois.items():
                r0,r1=roi["rows"]; c0,c1=roi["cols"]
                med = np.median(arr[r0:r1, c0:c1])
                ax.axvline(med, color=roi["color"], linestyle=":", linewidth=1.5,
                           label=f"{label}={med:.0f}")
            ax.set_xlabel("DN"); ax.legend(fontsize=8)
        else:
            disp = pct_stretch(arr)
            ax.imshow(disp, cmap="gray")
            for label,roi in rois.items():
                r0,r1=roi["rows"]; c0,c1=roi["cols"]
                ax.add_patch(patches.Rectangle((c0,r0),c1-c0,r1-r0,
                    linewidth=2,edgecolor=roi["color"],facecolor="none"))
                ax.text(c0,r0-8,label,color=roi["color"],fontsize=8,fontweight="bold")
            ax.axis("off")
        ax.set_title(title, fontsize=10)
    plt.tight_layout()
    pdf.savefig(fig, dpi=150); plt.close()

    # ── Page 6: Sensor assessment summary ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.suptitle("Sensor Assessment Summary", fontsize=16, fontweight="bold")
    ax.axis("off")

    rows = [["Sensor","Band","CWL (nm)","Black med","White med","Contrast","White %","Status"]]
    for idx,(name,cwl,_,_) in enumerate(RGB_BANDS):
        b = roi_stats(rgb[idx], RGB_ROIS["Black"])["median"]
        w = roi_stats(rgb[idx], RGB_ROIS["White"])["median"]
        c,p,s = assess(w, 4095, b)
        rows.append(["RGB",name,cwl,f"{b:.0f}",f"{w:.0f}",f"{c:.1f}x",f"{p:.0f}%",s])
    for idx,(name,cwl,_,_) in enumerate(BIO_BANDS):
        b = roi_stats(bio[idx], BIO_ROIS["Black"])["median"]
        w = roi_stats(bio[idx], BIO_ROIS["White"])["median"]
        c,p,s = assess(w, 4095, b)
        rows.append(["BIO",name,cwl,f"{b:.0f}",f"{w:.0f}",f"{c:.1f}x",f"{p:.0f}%",s])
    for arr,rois,sname,mdn in [(s1125,S1125_ROIS,"SWIR 1125",s1125.max()),
                                (s1275,S1275_ROIS,"SWIR 1275",s1275.max())]:
        b = roi_stats(arr, rois["Black"])["median"]
        w = roi_stats(arr, rois["White"])["median"]
        c,p,s = assess(w, mdn, b)
        rows.append([sname,"—","—",f"{b:.0f}",f"{w:.0f}",f"{c:.1f}x",f"{p:.0f}%",s])

    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", bbox=[0,0.25,1,0.7])
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    for (r,c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor("#2c3e50"); cell.set_text_props(color="white", fontweight="bold")
        else:
            status_val = rows[r][7]
            cell.set_facecolor("#f0f0f0" if r%2==0 else "white")
            if c == 7:
                cell.set_facecolor(COLORS.get(status_val, "white"))
                cell.set_text_props(fontweight="bold")
        cell.set_edgecolor("#cccccc")

    # Key findings
    findings = [
        "RGB: ALL bands SATURATED — white PE film hits 4095 DN (12-bit ceiling). Exposure time (246µs) cannot be reduced further.",
        "BIO (NIR): Requires investigation — results pending from manufacturer.",
        "SWIR 1125 & 1275: Well-exposed, good linearity, no saturation.",
        "SWIR 1275 is spatially shifted ~70px horizontally relative to SWIR 1125 — co-registration required.",
        "Black reference (metal car): specular surface, unknown reflectance — not suitable for quantitative radiometry.",
        "Manufacturer has not confirmed reflectance linearity fix before shipping the camera back.",
    ]
    ax.text(0.0, 0.22, "Key Findings:", fontsize=11, fontweight="bold", transform=ax.transAxes)
    for i, f in enumerate(findings):
        ax.text(0.01, 0.18-i*0.032, f"• {f}", fontsize=8.5, transform=ax.transAxes,
                wrap=True, va="top")
    pdf.savefig(fig, dpi=150); plt.close()

print(f"Report saved to {OUT_PDF}")
