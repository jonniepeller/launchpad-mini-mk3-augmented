# Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/novation/mixer.py
from __future__ import absolute_import, print_function, unicode_literals
from functools import partial
from future.moves.itertools import zip_longest
from ableton.v2.control_surface.components import MixerComponent as MixerComponentBase


class MixerComponent(MixerComponentBase):
    def __getattr__(self, name):
        if (
            name.startswith("set_")
            and (name.endswith("controls") or name.endswith("displays"))
            and not getattr(self, name[4:], None)
        ):
            return partial(self._set_controls_on_all_channel_strips, name[4:-1])
        raise AttributeError

    def _set_controls_on_all_channel_strips(self, attr_name, controls):
        for strip, control in zip_longest(self._channel_strips, controls or []):
            getattr(strip, attr_name).set_control_element(control)

    def set_static_color_value(self, value):
        for strip in self._channel_strips:
            strip.set_static_color_value(value)

    def set_send_controls(self, controls):
        num_sends = len(self._song.return_tracks)
        for channel_idx, channel_strip in enumerate(self._channel_strips):
            send_controls = []
            for send_idx in range(num_sends):
                if controls:
                    send_controls.append(controls.get_button(send_idx, channel_idx))
            channel_strip.set_send_controls(send_controls)

    def set_colored_mute_buttons(self, buttons):
        for strip, button in zip_longest(self._channel_strips, buttons or []):
            strip.set_mute_button(button)
