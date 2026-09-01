from pydub import AudioSegment


def get_wave_data(audio):
    samples = audio.get_array_of_samples()

    channels = audio.channels

    if channels > 1:
        samples = samples[::channels]

    return samples

def draw_wave(self, audio):

    self.wave.delete("all")

    samples = audio.get_array_of_samples()

    width = self.wave.winfo_width()
    height = self.wave.winfo_height()

    step = max(1, len(samples) // width)

    centre = height // 2

    for x in range(width):

        start = x * step
        end = min(start + step, len(samples))

        section = samples[start:end]

        if not section:
            continue

        maximum = max(abs(value) for value in section)

        y = int(
            maximum / 32768 * (height // 2)
        )

        self.wave.create_line(
            x,
            centre - y,
            x,
            centre + y
        )