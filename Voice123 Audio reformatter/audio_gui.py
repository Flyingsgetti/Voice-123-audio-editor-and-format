import os
import time
import subprocess
import tkinter as tk
from tkinter import messagebox

# Ensure folders exist
for folder in ["exported", "GUI exported"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class TimelineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice123 Audio Suite")
        self.root.geometry("900x540")
        self.root.configure(bg="#1e1e1e")

        self.clips = [] 
        self.load_clips()

        # Top Control Bar
        top_frame = tk.Frame(root, bg="#1e1e1e")
        top_frame.pack(fill="x", padx=15, pady=15)

        self.btn_format = tk.Button(top_frame, text="1. Format Imported Files (-3dB)", bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", command=self.run_format)
        self.btn_format.pack(side="left", padx=(0, 8))

        self.btn_play = tk.Button(top_frame, text="▶ Preview Play", bg="#ffc107", fg="black", font=("Segoe UI", 10, "bold"), relief="flat", command=self.run_preview)
        self.btn_play.pack(side="left", padx=(0, 4))

        self.btn_pause = tk.Button(top_frame, text="⏸ Pause", bg="#d9534f", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", command=self.run_pause)
        self.btn_pause.pack(side="left")

        # Equalize Volume Checkbox Option
        self.normalize_var = tk.BooleanVar(value=False)
        self.chk_normalize = tk.Checkbutton(root, text="Equalize Volume Across All Clips (-3dB Normalization)", variable=self.normalize_var, bg="#1e1e1e", fg="#ffffff", selectcolor="#252526", font=("Segoe UI", 9))
        self.chk_normalize.pack(anchor="w", padx=15, pady=(0, 5))

        # Horizontal Timeline Area
        tk.Label(root, text="Horizontal Timeline (Drag block body to reorder sequence | Drag right edge to add tail space):", bg="#1e1e1e", fg="#cccccc", font=("Segoe UI", 9)).pack(anchor="w", padx=15)

        self.canvas_frame = tk.Frame(root, bg="#252526", bd=1, relief="solid")
        self.canvas_frame.pack(fill="x", padx=15, pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, height=140, bg="#252526", highlightthickness=0)
        self.canvas.pack(fill="x", padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Bottom Export Final Action
        self.btn_stitch = tk.Button(root, text="3. Export Final to 'GUI exported' folder", bg="#28a745", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", command=self.run_stitch)
        self.btn_stitch.pack(fill="x", padx=15, pady=(10, 15))

        self.drag_mode = None  
        self.drag_index = None
        self.drag_start_x = 0
        self.preview_process = None
        self.last_compile_error = None
        self.redraw_timeline()

    def load_clips(self):
        self.clips = []
        if os.path.exists("exported"):
            for f in sorted(os.listdir("exported")):
                if f.endswith(".wav") and "_padded_" not in f and "Final_Audition" not in f and "_norm" not in f:
                    self.clips.append({'name': f, 'padding': 0.0, 'base_width': 110})

    def run_format(self):
        if os.path.exists("V123Convert.bat"):
            subprocess.run(['cmd.exe', '/c', 'V123Convert.bat'])
            messagebox.showinfo("Success", "Formatting complete!")
            self.load_clips()
            self.redraw_timeline()
        else:
            messagebox.showerror("Error", "V123Convert.bat not found!")

    def redraw_timeline(self):
        self.canvas.delete("all")
        start_x = 10
        y = 15
        height = 100

        for i, clip in enumerate(self.clips):
            extra_w = int(clip['padding'] * 30)
            w = clip['base_width'] + extra_w
            
            self.canvas.create_rectangle(start_x, y, start_x + w, y + height, fill="#005b96", outline="#4ec9b0", width=2)
            
            self.canvas.create_text(start_x + 10, y + 15, anchor="nw", text=f"#{i+1}", fill="#ffc107", font=("Segoe UI", 11, "bold"))
            display_name = clip['name'] if len(clip['name']) < 14 else clip['name'][:12] + ".."
            self.canvas.create_text(start_x + 10, y + 40, anchor="nw", text=display_name, fill="white", font=("Segoe UI", 9))
            
            if clip['padding'] > 0:
                self.canvas.create_text(start_x + 10, y + 70, anchor="nw", text=f"+{clip['padding']:.1f}s tail", fill="#85e3ff", font=("Segoe UI", 8, "italic"))

            self.canvas.create_line(start_x + w - 5, y, start_x + w - 5, y + height, fill="#ffffff", width=3)

            clip['x1'] = start_x
            clip['x2'] = start_x + w
            start_x += w + 10

        self.canvas.config(scrollregion=(0, 0, start_x + 20, 140))

    def on_canvas_click(self, event):
        for i, clip in enumerate(self.clips):
            if clip['x1'] <= event.x <= clip['x2'] and 15 <= event.y <= 115:
                self.drag_index = i
                self.drag_start_x = event.x
                if event.x >= clip['x2'] - 15:
                    self.drag_mode = 'resize'
                else:
                    self.drag_mode = 'reorder'
                break

    def on_canvas_drag(self, event):
        if self.drag_index is not None:
            if self.drag_mode == 'resize':
                diff = event.x - self.drag_start_x
                added_secs = max(0.0, round(diff / 30.0, 1))
                self.clips[self.drag_index]['padding'] = added_secs
                self.redraw_timeline()
            elif self.drag_mode == 'reorder':
                for i, clip in enumerate(self.clips):
                    mid = (clip['x1'] + clip['x2']) / 2
                    if event.x < mid and self.drag_index > i:
                        item = self.clips.pop(self.drag_index)
                        self.clips.insert(i, item)
                        self.drag_index = i
                        self.redraw_timeline()
                        break
                    elif event.x > mid and self.drag_index < i:
                        item = self.clips.pop(self.drag_index)
                        self.clips.insert(i, item)
                        self.drag_index = i
                        self.redraw_timeline()
                        break

    def on_canvas_release(self, event):
        self.drag_index = None
        self.drag_mode = None
        self.redraw_timeline()

    @staticmethod
    def _concat_escape(filename):
        """Escape a filename for an ffmpeg concat-demuxer 'file' line.
        The concat demuxer only understands single-quote grouping, and a
        literal single quote inside a quoted field must be written as the
        sequence '\\'' (close quote, escaped quote, reopen quote). Double
        quotes are NOT treated as quoting by this parser at all."""
        return filename.replace("'", "'\\''")

    def _run_ffmpeg(self, cmd, step_desc):
        """Run an ffmpeg command, capture stderr, and raise with the real
        reason on failure instead of silently swallowing it."""
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"{step_desc} failed (ffmpeg exit {result.returncode}):\n{result.stderr.strip()[-800:]}")

    def compile_track_to_path(self, output_filepath):
        self.last_compile_error = None
        if not self.clips:
            self.last_compile_error = "No clips available."
            return False

        # Remove any stale copy of this exact output path first, so a failed
        # write below can never be mistaken for a successful (old) one.
        if os.path.exists(output_filepath):
            try:
                os.remove(output_filepath)
            except OSError:
                pass

        list_path = os.path.abspath(os.path.join("exported", f"file_list_{int(time.time()*1000)}.txt"))
        try:
            with open(list_path, "w", encoding="utf-8", newline="\n") as f:
                for clip in self.clips:
                    orig_file = clip['name']
                    pad_secs = clip['padding']

                    target_file = orig_file
                    if self.normalize_var.get():
                        norm_filename = orig_file.replace(".wav", "_norm.wav")
                        full_norm_path = os.path.join("exported", norm_filename)
                        if not os.path.exists(full_norm_path):
                            orig_path = os.path.join("exported", orig_file)
                            norm_cmd = ['ffmpeg', '-y', '-i', orig_path, '-af', 'volume=-3dB', '-ar', '44100', '-ac', '1', full_norm_path]
                            self._run_ffmpeg(norm_cmd, f"Normalizing {orig_file}")
                        target_file = norm_filename

                    if pad_secs > 0.0:
                        clean_name = target_file.replace(".wav", "")
                        padded_filename = f"{clean_name}_padded_{str(pad_secs).replace('.', '_')}.wav"
                        full_padded_path = os.path.join("exported", padded_filename)

                        if not os.path.exists(full_padded_path):
                            target_path = os.path.join("exported", target_file)
                            cmd = [
                                'ffmpeg', '-y', '-i', target_path,
                                '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(pad_secs),
                                '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1[out]',
                                '-map', '[out]', '-acodec', 'pcm_s16le', full_padded_path
                            ]
                            self._run_ffmpeg(cmd, f"Padding {target_file}")

                        f.write(f"file '{self._concat_escape(padded_filename)}'\n")
                    else:
                        f.write(f"file '{self._concat_escape(target_file)}'\n")

            concat_cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_path, '-c', 'copy', output_filepath]
            self._run_ffmpeg(concat_cmd, "Stitching final track")

            if not os.path.exists(output_filepath):
                raise RuntimeError("ffmpeg reported success but the output file was not created.")

            return True
        except Exception as e:
            self.last_compile_error = str(e)
            return False
        finally:
            if os.path.exists(list_path):
                os.remove(list_path)

    def run_preview(self):
        self.run_pause()
        # Millisecond-precision name (matches list_path). The old int(time.time())
        # version truncated to whole seconds, so two previews fired within the
        # same second reused the SAME filename. Combined with terminate() not
        # waiting for the prior PowerShell player to actually release its file
        # handle, the overwrite could silently fail and the OLD preview (from
        # before you reordered) would just get replayed.
        preview_path = os.path.abspath(os.path.join("GUI exported", f"preview_{int(time.time()*1000)}.wav"))

        success = self.compile_track_to_path(preview_path)
        if success:
            try:
                ps_command = f"(New-Object Media.SoundPlayer '{preview_path}').PlaySync();"
                self.preview_process = subprocess.Popen(['powershell', '-Command', ps_command], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", self.last_compile_error or "No clips available to preview!")

    def run_pause(self):
        try:
            if self.preview_process and self.preview_process.poll() is None:
                self.preview_process.terminate()
                try:
                    # Wait for the process (and, practically, its file handle
                    # on the WAV it was playing) to actually release before
                    # anything tries to overwrite that file.
                    self.preview_process.wait(timeout=1.5)
                except subprocess.TimeoutExpired:
                    self.preview_process.kill()
                    self.preview_process.wait(timeout=1.5)
            subprocess.run(['powershell', '-Command', "Stop-Process -Name 'powershell' -ErrorAction SilentlyContinue"], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def run_stitch(self):
        final_output = os.path.abspath(os.path.join("GUI exported", "Final_Audition.wav"))
        success = self.compile_track_to_path(final_output)
        if success:
            messagebox.showinfo("Success", "Final master track exported successfully to 'GUI exported\\Final_Audition.wav'!")
        else:
            messagebox.showerror("Error", self.last_compile_error or "No clips available to export.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimelineApp(root)
    root.mainloop()