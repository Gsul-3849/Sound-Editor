from pydub import AudioSegment


def get_wave_data(audio):
    samples = audio.get_array_of_samples()

    if audio.channels > 1:
        samples = samples[::audio.channels]

    return samples


def draw_wave(self, audio):
    self.wave.delete("all")

    samples = get_wave_data(audio)
    width = max(1, self.wave.winfo_width())
    height = max(1, self.wave.winfo_height())

    if not samples:
        return

    centre_y = height // 2

    samples_per_x = max(1, len(samples) // width)

    for x in range(width):
        start = x * samples_per_x
        end = min(start + samples_per_x, len(samples))
        section = samples[start:end]

        if not section:
            continue

        max_value = max(abs(value) for value in section)
        amplitude = int(max_value / 32768 * centre_y)

        self.wave.create_line(
            x,
            centre_y - amplitude,
            x,
            centre_y + amplitude,
            fill="dodgerblue"
        )

    self.wave.create_line(
        0,
        centre_y,
        width,
        centre_y,
        fill="#d0d0d0"
    )