from novation.mixer import MixerComponent


class MixerComponentAugmented(MixerComponent):
    def set_send_controls(self, controls):
        # 7 rows for sends (bottom row is mute buttons)
        num_sends = 7
        for channel_idx, channel_strip in enumerate(self._channel_strips):
            send_controls = []
            for send_idx in range(num_sends):
                if controls:
                    send_controls.append(controls.get_button(send_idx, channel_idx))
            channel_strip.set_send_controls(send_controls)
