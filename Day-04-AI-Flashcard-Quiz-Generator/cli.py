"""
Day 04 - AI Flashcard & Quiz Generator (CLI Interactive Game & Viewer)
Belajar dan bermain kuis interaktif langsung dari terminal.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from generator import generate_study_deck, export_to_anki_csv, StudyDeck

console = Console()

def play_flashcards(deck: StudyDeck):
    console.print()
    console.rule(f"[bold cyan]📇 FLASHCARDS: {deck.topic_title.upper()}[/bold cyan]")
    console.print(f"[dim]Total: {len(deck.flashcards)} kartu. Tekan Enter untuk melihat sisi belakang.[/dim]\n")

    for idx, card in enumerate(deck.flashcards, 1):
        # Front of Card
        hint_text = f"\n[dim italic]💡 Hint: {card.hint}[/dim italic]" if card.hint else ""
        console.print(Panel(
            f"[bold yellow]{card.front}[/bold yellow]{hint_text}",
            title=f"[cyan]Kartu #{idx} / {len(deck.flashcards)} ({card.category_tag})[/cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        Prompt.ask("[dim]Tekan Enter untuk membalik kartu...[/dim]", default="")

        # Back of Card
        console.print(Panel(
            f"[bold green]{card.back}[/bold green]",
            title="[green]Sisi Belakang (Jawaban)[/green]",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()

def play_quiz(deck: StudyDeck):
    console.print()
    console.rule(f"[bold magenta]🎮 INTERACTIVE QUIZ: {deck.topic_title.upper()}[/bold magenta]")
    console.print(f"[dim]Jawab setiap pertanyaan dengan mengetik A, B, C, atau D.[/dim]\n")

    score = 0
    total = len(deck.quiz)

    for q in deck.quiz:
        console.print(f"[bold cyan]Pertanyaan #{q.question_number} / {total}[/bold cyan] [yellow]({q.difficulty})[/yellow]")
        console.print(Panel(f"[bold white]{q.question}[/bold white]", border_style="blue"))

        for opt in q.options:
            console.print(f"  [bold yellow]{opt.id}.[/bold yellow] {opt.text}")

        console.print()
        user_choice = Prompt.ask("Jawaban Anda", choices=["A", "B", "C", "D", "a", "b", "c", "d"]).upper()

        if user_choice == q.correct_option_id:
            console.print("[bold green]✅ BENAR![/bold green]")
            score += 1
        else:
            console.print(f"[bold red]❌ KURANG TEPAT![/bold red] Jawaban yang benar adalah [bold green]{q.correct_option_id}[/bold green].")

        console.print(Panel(
            f"[dim]{q.explanation}[/dim]",
            title="[dim]Penjelasan[/dim]",
            border_style="dim"
        ))
        console.print()

    # Final Score
    percentage = (score / total) * 100
    grade_color = "green" if percentage >= 80 else "yellow" if percentage >= 60 else "red"
    console.rule("[bold]🏁 HASIL AKHIR KUIS[/bold]")
    console.print(f"\nSkor Anda: [{grade_color} bold]{score} dari {total} ({percentage:.0f}%)[/{grade_color} bold]")
    
    if percentage == 100:
        console.print("[bold green]🏆 Sempurna! Anda menguasai materi ini sepenuhnya![/bold green]\n")
    elif percentage >= 70:
        console.print("[bold yellow]👍 Kerja bagus! Terus tingkatkan pemahaman Anda![/bold yellow]\n")
    else:
        console.print("[bold red]📚 Disarankan untuk mengulang kembali materi flashcard.[/bold red]\n")

def main():
    parser = argparse.ArgumentParser(description="AI Flashcard & Quiz Generator CLI")
    parser.add_argument("-f", "--file", help="Path ke file materi pembelajaran (.txt / .md)")
    parser.add_argument("-t", "--topic", help="Topik materi langsung (misal: 'Dasar Jaringan Komputer')")
    parser.add_argument("-c", "--cards", type=int, default=5, help="Jumlah flashcards (default: 5)")
    parser.add_argument("-q", "--questions", type=int, default=5, help="Jumlah soal kuis (default: 5)")
    parser.add_argument("-d", "--difficulty", default="Medium", choices=["Easy", "Medium", "Hard"], help="Tingkat kesulitan")
    parser.add_argument("--anki-out", help="Export flashcards ke file format Anki (.tsv/.txt)")
    parser.add_argument("--json-out", help="Export seluruh deck ke file JSON")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    content = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File '{args.file}' tidak ditemukan!")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
    elif args.topic:
        content = f"Topik Pembelajaran: {args.topic}"
    else:
        console.print(Panel.fit(
            "[bold cyan]📇 AI Flashcard & Quiz Generator (Day 04)[/bold cyan]\n"
            "[dim]Masukkan materi/catatan Anda, lalu tekan Ctrl+Z (Windows) atau Ctrl+D (Mac/Linux) lalu Enter:[/dim]",
            border_style="cyan"
        ))
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operasi dibatalkan.[/yellow]")
            sys.exit(0)

    if not content.strip():
        console.print("[bold red]Teks materi kosong.[/bold red]")
        sys.exit(1)

    with console.status("[bold green]Sedang menghasilkan Flashcards & Kuis AI...[/bold green]", spinner="dots"):
        try:
            deck: StudyDeck = generate_study_deck(
                content=content,
                num_cards=args.cards,
                num_questions=args.questions,
                difficulty=args.difficulty,
                model_name=args.model
            )
        except Exception as e:
            console.print(f"[bold red]Gagal menghasilkan study deck:[/bold red] {e}")
            sys.exit(1)

    # Export jika diminta
    if args.anki_out:
        anki_tsv = export_to_anki_csv(deck)
        Path(args.anki_out).write_text(anki_tsv, encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] Anki deck diexport ke: [cyan]{args.anki_out}[/cyan]")

    if args.json_out:
        Path(args.json_out).write_text(deck.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] JSON data diexport ke: [cyan]{args.json_out}[/cyan]")

    # Mode Interaktif
    console.print(f"\n[bold green]Deck Berhasil Dibuat:[/bold green] [bold cyan]{deck.topic_title}[/bold cyan]")
    console.print(f"[dim]{deck.summary}[/dim]\n")

    mode = Prompt.ask("Pilih Mode", choices=["1", "2", "3"], default="1")
    if mode == "1":
        play_flashcards(deck)
        play_quiz(deck)
    elif mode == "2":
        play_flashcards(deck)
    elif mode == "3":
        play_quiz(deck)

if __name__ == "__main__":
    main()
