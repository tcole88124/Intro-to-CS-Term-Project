def main():
    """
    Entry point of the program.
    Creates the DJAssistant object and starts the program.
    """
    print("Starting DJ Assistant")
    assistant = DJAssistant("songs.csv")
    assistant.run()


# -----------------------------
# Terminal styling (makes it "pretty")
# -----------------------------
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    def color(text, *codes):
        return "".join(codes) + str(text) + Style.RESET


def banner():
    print(Style.color("\n" + "═" * 52, Style.CYAN))
    print(Style.color("   🎧 DJ Song Selector Assistant 🎧", Style.BOLD, Style.CYAN))
    print(Style.color("═" * 52 + "\n", Style.CYAN))


# -----------------------------
# Data model
# -----------------------------
class Song:
    """
    Represents a single song with its attributes.
    Each row from the CSV file becomes a Song object.
    """
    def __init__(self, title, artist, genre, bpm, energy):
        self.title = title.strip()
        self.artist = artist.strip()
        self.genre = genre.strip()

        # Convert BPM/energy safely
        self.bpm = Song._safe_int(bpm, default=0)
        self.energy = Song._safe_int(energy, default=3)

        # Keep energy on a 1–5 scale (as you requested)
        if self.energy < 1:
            self.energy = 1
        if self.energy > 5:
            self.energy = 5

    def _safe_int(value, default=0):
        try:
            return int(str(value).strip())
        except ValueError:
            return default

    def key(self):
        """
        Used to detect duplicates.
        (title + artist) is a good "unique key" for this project.
        """
        return (self.title.lower(), self.artist.lower())

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.genre}, {self.bpm} BPM, E{self.energy})"


# -----------------------------
# Main logic
# -----------------------------
class DJAssistant:
    """
    Main class that manages songs, user interaction,
    and song recommendations.
    """
    def __init__(self, filename):
        self.songs = []              # List to store Song objects
        self.load_songs(filename)    # Load songs from CSV file

    def load_songs(self, filename):
        """
        Loads song data from a CSV file and converts each row into a Song object.

        IMPORTANT FIXES:
        - Skips header lines anywhere in the file (not just the first line)
        - Handles extra commas in the TITLE by parsing from the right
        - Ignores blank lines
        - Automatically removes duplicates (same title + artist)
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                raw_lines = file.readlines()

            unique = set()
            loaded = 0
            skipped = 0

            for line in raw_lines:
                line = line.strip()
                if not line:
                    continue

                # If someone pasted the header multiple times, skip it
                lower = line.lower().replace(" ", "")
                if lower == "title,artist,genre,bpm,energy":
                    continue

                # Split by comma (your file is plain comma-separated)
                parts = [p.strip() for p in line.split(",")]

                # Sometimes titles have commas (ex: "My Neck, My Back")
                # That creates MORE than 5 columns.
                # We'll parse from RIGHT:
                # last = energy, second last = bpm, third last = genre
                # remaining left side contains "title,artist" (title may include commas)
                if len(parts) < 5:
                    skipped += 1
                    continue

                # Pull last 3 guaranteed fields
                energy = parts[-1]
                bpm = parts[-2]
                genre = parts[-3]

                # Skip any accidental "bpm"/"energy" text rows
                if str(bpm).strip().lower() == "bpm" or str(energy).strip().lower() == "energy":
                    continue

                # Rebuild the left side which should contain title + artist
                left = ",".join(parts[:-3])

                # Now split left into title + artist by the FIRST comma only
                if "," not in left:
                    skipped += 1
                    continue

                title, artist = left.split(",", 1)

                song = Song(title, artist, genre, bpm, energy)

                # If BPM failed to parse (0), skip it (bad row)
                if song.bpm == 0:
                    skipped += 1
                    continue

                # Remove duplicates (same title + artist)
                k = song.key()
                if k in unique:
                    continue

                unique.add(k)
                self.songs.append(song)
                loaded += 1

            # If file was empty/bad
            if not self.songs:
                print(Style.color("Error: No valid songs loaded. Check songs.csv format.", Style.RED))
                exit()

            print(Style.color(f"Loaded {loaded} songs (duplicates auto-removed).", Style.GREEN))
            if skipped > 0:
                print(Style.color(f"Skipped {skipped} bad/invalid lines.", Style.YELLOW))

        except FileNotFoundError:
            print(Style.color("Error: songs.csv file not found.", Style.RED))
            exit()

    def choose_song(self, filtered_songs):
        """
        Displays songs and lets the user choose the current track.
        """
        print(Style.color("Available Songs:", Style.BOLD, Style.WHITE))
        for i, song in enumerate(filtered_songs):
            print(f"{Style.color(str(i+1).rjust(2), Style.CYAN)}. "
                  f"{song.title} {Style.color('-', Style.DIM)} {song.artist} "
                  f"{Style.color(f'({song.genre}, {song.bpm} BPM, E{song.energy})', Style.DIM)}")

        while True:
            choice = input(Style.color("\nChoose current song number: ", Style.YELLOW)).strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(filtered_songs):
                    return filtered_songs[idx - 1]
            print(Style.color("Invalid choice. Try again.", Style.RED))

    def choose_genre_filter(self):
        """
        Optional: let user filter by genre to make the list easier to navigate.
        (You can just press Enter to skip.)
        """
        genres = sorted(set(song.genre for song in self.songs))
        print(Style.color("Genres found:", Style.BOLD, Style.WHITE))
        print(Style.color(", ".join(genres), Style.DIM))

        g = input(Style.color("\nType a genre to filter (or press Enter for ALL): ", Style.YELLOW)).strip()
        if not g:
            return None

        # Match case-insensitively
        for real in genres:
            if real.lower() == g.lower():
                return real

        print(Style.color("Genre not found. Showing ALL songs.", Style.YELLOW))
        return None

    def choose_energy_goal(self):
        """
        Ask user if they want energy to go up/down/same.
        """
        goal = input(Style.color("Energy goal (up / down / same): ", Style.YELLOW)).strip().lower()
        if goal not in ["up", "down", "same"]:
            print(Style.color("Invalid option — using 'same'.", Style.YELLOW))
            goal = "same"
        return goal

    def recommend(self, current_song, goal, pool):
        """
        Scores and ranks songs based on:
        - BPM closeness
        - Energy direction (up/down/same)
        - Genre match bonus

        Returns top 5 + a "why" explanation for each recommendation.
        """
        recommendations = []

        for song in pool:
            if song.key() == current_song.key():
                continue  # skip current song

            bpm_diff = abs(song.bpm - current_song.bpm)
            energy_diff = song.energy - current_song.energy

            # Score closer BPM higher (DJ realism)
            score = 100 - (bpm_diff * 2)

            # Energy direction bonus
            if goal == "up":
                if energy_diff > 0:
                    score += 20
                else:
                    score -= 5
            elif goal == "down":
                if energy_diff < 0:
                    score += 20
                else:
                    score -= 5
            else:  # same
                if energy_diff == 0:
                    score += 10

            # Genre bonus
            if song.genre.lower() == current_song.genre.lower():
                score += 10

            # Build an explanation (helps your presentation)
            why = []
            why.append(f"BPM diff: {bpm_diff}")
            if goal != "same":
                why.append(f"Energy change: {energy_diff:+d} (goal: {goal})")
            else:
                why.append(f"Energy: {song.energy} (goal: same)")
            if song.genre.lower() == current_song.genre.lower():
                why.append("Genre match: +10")

            recommendations.append((score, song, "; ".join(why)))

        recommendations.sort(reverse=True, key=lambda x: x[0])
        return recommendations[:5]

    def run(self):
        """
        Controls the main flow of the program.
        """
        banner()

        # Optional: filter by genre (makes it easier during demo)
        genre_filter = self.choose_genre_filter()
        if genre_filter:
            pool = [s for s in self.songs if s.genre == genre_filter]
            if not pool:  # safety fallback
                pool = self.songs
        else:
            pool = self.songs

        # Choose current song
        current_song = self.choose_song(pool)
        print(Style.color("\nNow playing:", Style.DIM) + " " +
              Style.color(str(current_song), Style.BOLD, Style.GREEN))

        # Choose energy goal
        goal = self.choose_energy_goal()

        # Recommend next songs
        results = self.recommend(current_song, goal, pool)

        # Display results (pretty + explains WHY)
        print(Style.color("\nRecommended Next Songs:", Style.BOLD, Style.MAGENTA))
        for i, (score, song, why) in enumerate(results, start=1):
            print(Style.color(f"{i}.", Style.CYAN),
                  f"{Style.color(song.title, Style.BOLD)} by {song.artist} "
                  f"{Style.color(f'({song.bpm} BPM, E{song.energy})', Style.DIM)}")
            print(Style.color("   why:", Style.DIM), Style.color(why, Style.DIM))
            print(Style.color("   score:", Style.DIM), Style.color(score, Style.DIM))

        print(Style.color("\nDone. Run again to try a different song.\n", Style.CYAN))


if __name__ == "__main__":
    main()
