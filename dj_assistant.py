import csv

print("Starting DJ Assistant")


def main():
    """
    Entry point of the program.
    Creates the DJAssistant object and starts the program.
    """
    assistant = DJAssistant("songs.csv")
    assistant.run()


class Song:
    """
    Represents a single song with its attributes.
    Each row from the CSV file becomes a Song object.
    """
    def __init__(self, title, artist, genre, bpm, energy):
        # Defensive programming: skip bad numeric data
        if not bpm.isdigit() or not energy.isdigit():
            raise ValueError("Invalid BPM or energy")

        self.title = title
        self.artist = artist
        self.genre = genre
        self.bpm = int(bpm)
        self.energy = int(energy)


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
        Loads song data from a CSV file and converts
        each row into a Song object.
        """
        try:
            with open(filename, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)

                # Skip the first header row
                next(reader, None)

                for row in reader:
                    # Skip malformed rows
                    if len(row) != 5:
                        continue

                    title, artist, genre, bpm, energy = row

                    try:
                        self.songs.append(
                            Song(title, artist, genre, bpm, energy)
                        )
                    except ValueError:
                        # Skip rows with bad BPM/energy (extra headers, blanks)
                        continue

        except FileNotFoundError:
            print("Error: songs.csv file not found.")
            exit()

    def choose_song(self):
        """
        Displays available songs and allows the user
        to choose the current track.
        """
        print("\nAvailable Songs:")
        for i, song in enumerate(self.songs):
            print(f"{i + 1}. {song.title} - {song.artist}")

        while True:
            choice = input("Choose current song number: ")
            if choice.isdigit() and 1 <= int(choice) <= len(self.songs):
                return self.songs[int(choice) - 1]
            print("Invalid choice. Please try again.")

    def recommend(self, current_song, goal):
        """
        Scores and ranks songs based on BPM difference,
        energy change, and genre compatibility.
        """
        recommendations = []

        for song in self.songs:
            if song == current_song:
                continue

            bpm_difference = abs(song.bpm - current_song.bpm)
            energy_difference = song.energy - current_song.energy

            score = 100 - (bpm_difference * 2)

            if goal == "up" and energy_difference > 0:
                score += 20
            elif goal == "down" and energy_difference < 0:
                score += 20

            if song.genre == current_song.genre:
                score += 10

            recommendations.append((score, song))

        recommendations.sort(reverse=True, key=lambda x: x[0])
        return recommendations[:3]

    def run(self):
        """
        Controls the main flow of the program.
        """
        print("🎧 DJ Song Selector Assistant 🎧")

        current_song = self.choose_song()

        goal = input("Energy goal (up / down / same): ").lower()
        if goal not in ["up", "down", "same"]:
            goal = "same"

        results = self.recommend(current_song, goal)

        print("\nRecommended Next Songs:")
        for score, song in results:
            print(f"- {song.title} by {song.artist} ({song.bpm} BPM)")


if __name__ == "__main__":
    main()
