"""
Day 06 - AI Audio Meeting Transcriber & Minutes Summarizer (CLI Version)
Mentranskripsikan file rekaman audio dan membuat notulen rapat instan dari terminal.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from transcriber import process_meeting_audio, process_meeting_text_transcript, MeetingMinutes

console = Console()

PRIORITY_COLORS = {
    "High": "bold red",
    "Medium": "bold yellow",
    "Low": "bold green"
}

def display_meeting_minutes(minutes: MeetingMinutes):
    console.print()
    console.rule(f"[bold cyan]📋 NOTULEN RAPAT: {minutes.meeting_title.upper()}[/bold cyan]")
    console.print()

    # Metadata & Executive Summary
    attendees_str = ", ".join([f"[cyan]{a}[/cyan]" for a in minutes.attendees]) if minutes.attendees else "-"
    meta_md = f"""- **Tanggal:** {minutes.meeting_date or '-'} | **Durasi:** {minutes.duration_estimate or '-'}
- **Peserta Rapat:** {attendees_str}
- **Suasana & Tone:** `[yellow]{minutes.overall_sentiment_and_tone}[/yellow]`

### 📝 Ringkasan Eksekutif:
{minutes.executive_summary}
"""
    console.print(Panel(Markdown(meta_md), title="[bold green]🏛️ Informasi Rapat[/bold green]", border_style="green"))
    console.print()

    # Key Decisions
    if minutes.key_decisions:
        decisions_md = "\n".join([f"- ✅ **{d}**" for d in minutes.key_decisions])
        console.print(Panel(Markdown(decisions_md), title="[bold cyan]🎯 Keputusan Kunci yang Disepakati[/bold cyan]", border_style="cyan"))
        console.print()

    # Action Items Table
    if minutes.action_items:
        table = Table(title="⚡ Action Items & Tindak Lanjut", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("No", width=5, justify="center")
        table.add_column("Tugas / Tindakan", style="white")
        table.add_column("PIC / Assignee", width=22, style="bold cyan")
        table.add_column("Prioritas", width=12, justify="center")
        table.add_column("Tenggat Waktu", width=18, style="yellow")

        for idx, item in enumerate(minutes.action_items, 1):
            p_color = PRIORITY_COLORS.get(item.priority, "white")
            p_badge = f"[{p_color}]{item.priority}[/{p_color}]"
            table.add_row(str(idx), item.task, item.assignee, p_badge, item.deadline or "-")

        console.print(table)
        console.print()

    # Discussion Topics
    if minutes.discussion_topics:
        topics_md = ""
        for t in minutes.discussion_topics:
            speakers = ", ".join(t.key_speakers) if t.key_speakers else "Semua"
            topics_md += f"#### 🔹 {t.topic_name} *(Pembicara: {speakers})*\n{t.summary}\n\n"
        console.print(Panel(Markdown(topics_md), title="[bold yellow]🗣️ Rincian Pembahasan Topik[/bold yellow]", border_style="yellow"))
        console.print()

def main():
    parser = argparse.ArgumentParser(description="AI Audio Meeting Transcriber & Minutes Summarizer CLI")
    parser.add_argument("-a", "--audio", help="Path ke file audio (.mp3, .wav, .m4a, .ogg, .flac)")
    parser.add_argument("-t", "--transcript", help="Path ke file teks transkrip / catatan meeting")
    parser.add_argument("--md-out", help="Path untuk menyimpan notulen rapat dalam format Markdown")
    parser.add_argument("--json-out", help="Path untuk menyimpan hasil dalam format JSON")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    result: MeetingMinutes = None

    if args.audio:
        audio_p = Path(args.audio)
        if not audio_p.exists():
            console.print(f"[bold red]Error:[/bold red] File audio '{audio_p}' tidak ditemukan!")
            sys.exit(1)

        with console.status("[bold green]Mentranskripsikan audio & menyusun notulen dengan Gemini AI...[/bold green]", spinner="dots"):
            try:
                result = process_meeting_audio(audio_p, model_name=args.model)
            except Exception as e:
                console.print(f"[bold red]Gagal memproses audio:[/bold red] {e}")
                sys.exit(1)

    elif args.transcript:
        txt_p = Path(args.transcript)
        if not txt_p.exists():
            console.print(f"[bold red]Error:[/bold red] File transkrip '{txt_p}' tidak ditemukan!")
            sys.exit(1)
        
        content = txt_p.read_text(encoding="utf-8")
        with console.status("[bold green]Menganalisis teks meeting & mengekstrak action items...[/bold green]", spinner="dots"):
            try:
                result = process_meeting_text_transcript(content, model_name=args.model)
            except Exception as e:
                console.print(f"[bold red]Gagal memproses transkrip:[/bold red] {e}")
                sys.exit(1)
    else:
        # Default fallback to sample transcript
        sample_txt = Path(__file__).parent / "sample_meeting_transcript.txt"
        if sample_txt.exists():
            console.print(f"[yellow]Tidak ada argumen input. Menjalankan sample meeting:[/yellow] [cyan]{sample_txt.name}[/cyan]\n")
            content = sample_txt.read_text(encoding="utf-8")
            with console.status("[bold green]Menganalisis sample meeting...[/bold green]", spinner="dots"):
                result = process_meeting_text_transcript(content, model_name=args.model)
        else:
            console.print("[bold red]Gunakan `-a <file_audio>` atau `-t <file_transkrip>`.[/bold red]")
            sys.exit(1)

    display_meeting_minutes(result)

    # Export
    if args.md_out:
        md_text = f"""# Notulen Rapat: {result.meeting_title}
- **Tanggal:** {result.meeting_date or '-'} | **Durasi:** {result.duration_estimate or '-'}
- **Peserta:** {', '.join(result.attendees)}
- **Tone:** {result.overall_sentiment_and_tone}

## Ringkasan Eksekutif
{result.executive_summary}

## Keputusan Kunci
{chr(10).join(['- ' + d for d in result.key_decisions])}

## Action Items
| No | Tugas | PIC | Prioritas | Deadline |
|:---:|:---|:---|:---:|:---|
"""
        for idx, it in enumerate(result.action_items, 1):
            md_text += f"| {idx} | {it.task} | {it.assignee} | {it.priority} | {it.deadline or '-'} |\n"

        md_text += f"\n## Transkrip Lengkap\n\n{result.full_transcript}\n"
        Path(args.md_out).write_text(md_text, encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] Notulen Markdown disimpan ke: [cyan]{args.md_out}[/cyan]")

    if args.json_out:
        Path(args.json_out).write_text(result.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] JSON disimpan ke: [cyan]{args.json_out}[/cyan]")

if __name__ == "__main__":
    main()
