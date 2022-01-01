import logging

from ableton.v2.base import listens
from ableton.v2.control_surface import Layer, merge_skins
from ableton.v2.control_surface.components import SessionOverviewComponent
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent
from ableton.v2.control_surface.skin import Skin
from Launchpad_Mini_MK3 import sysex_ids as ids
from Launchpad_Mini_MK3.elements import Elements
from Launchpad_Mini_MK3.notifying_background import NotifyingBackgroundComponent
from Launchpad_Mini_MK3.skin import skin as default_mk3_skin
from novation import sysex
from novation.colors import Rgb
from novation.session_modes import SessionModesComponent
from novation.skin import Colors

from .novation_base_augmented import NovationBase

logger = logging.getLogger(__name__)


class AugmentedColors(Colors):
    class Mixer(Colors.Mixer):
        SendControls = Rgb.PURPLE

    class Mode(Colors.Mode):
        class Launch(object):
            On = Rgb.ORANGE

    class Session(Colors.Session):
        RecordButton = Rgb.ORANGE


augmented_skin = merge_skins(*(default_mk3_skin, Skin(AugmentedColors)))


class Launchpad_Mini_MK3_Augmented(NovationBase):

    model_family_code = ids.LP_MINI_MK3_FAMILY_CODE
    element_class = Elements
    skin = augmented_skin

    def __init__(self, *a, **k):
        self._last_layout_byte = sysex.SESSION_LAYOUT_BYTE
        super().__init__(*a, **k)

    def on_identified(self, midi_bytes):
        self._elements.firmware_mode_switch.send_value(sysex.DAW_MODE_BYTE)
        self._elements.layout_switch.send_value(self._last_layout_byte)
        super().on_identified(midi_bytes)

    def _create_components(self):
        super()._create_components()
        self._create_background()
        self._create_stop_solo_mute_modes()
        self._create_session_modes()
        self.__on_layout_switch_value.subject = self._elements.layout_switch

    def _create_session_layer(self):
        return super()._create_session_layer() + Layer(
            scene_launch_buttons="scene_launch_buttons"
        )

    def _create_stop_solo_mute_modes(self):
        self._stop_solo_mute_modes = ModesComponent(
            name=u"Stop_Solo_Mute_Modes",
            is_enabled=False,
            support_momentary_mode_cycling=False,
            layer=Layer(cycle_mode_button=self._elements.scene_launch_buttons_raw[7]),
        )
        num_sends = len(self._mixer._song.return_tracks)
        send_rows = self._elements.clip_launch_matrix.submatrix[:, (8 - num_sends) : 8]
        bottom_row = self._elements.clip_launch_matrix.submatrix[:, 7:8]
        self._stop_solo_mute_modes.add_mode(
            u"launch",
            None,
            cycle_mode_button_color=u"Mode.Launch.On",
        )
        self._stop_solo_mute_modes.add_mode(
            u"stop",
            AddLayerMode(self._session, Layer(stop_track_clip_buttons=bottom_row)),
            cycle_mode_button_color=u"Session.StopClip",
        )
        self._stop_solo_mute_modes.add_mode(
            u"solo",
            AddLayerMode(self._mixer, Layer(solo_buttons=bottom_row)),
            cycle_mode_button_color=u"Mixer.SoloOn",
        )
        self._stop_solo_mute_modes.add_mode(
            u"mute",
            AddLayerMode(self._mixer, Layer(mute_buttons=bottom_row)),
            cycle_mode_button_color=u"Mixer.MuteOff",
        )
        self._stop_solo_mute_modes.add_mode(
            u"sends",
            AddLayerMode(self._mixer, Layer(send_controls=send_rows)),
            cycle_mode_button_color=u"Mixer.SendControls",
        )
        self._stop_solo_mute_modes.selected_mode = u"sends"
        self._stop_solo_mute_modes.set_enabled(True)

    def _create_session_modes(self):
        self._session_overview = SessionOverviewComponent(
            name="Session_Overview",
            is_enabled=False,
            session_ring=self._session_ring,
            enable_skinning=True,
            layer=Layer(button_matrix="clip_launch_matrix"),
        )
        self._session_modes = SessionModesComponent(
            name="Session_Modes",
            is_enabled=False,
            layer=Layer(
                cycle_mode_button="session_mode_button",
                mode_button_color_control="session_button_color_element",
            ),
        )
        self._session_modes.add_mode(u"launch", None)
        self._session_modes.add_mode(
            "overview",
            (
                self._session_overview,
                AddLayerMode(
                    self._session_navigation,
                    Layer(
                        page_up_button="up_button",
                        page_down_button="down_button",
                        page_left_button="left_button",
                        page_right_button="right_button",
                    ),
                ),
                AddLayerMode(
                    self._background,
                    Layer(scene_launch_buttons="scene_launch_buttons"),
                ),
            ),
        )
        self._session_modes.selected_mode = "launch"
        self._session_modes.set_enabled(True)
        self.__on_session_mode_changed.subject = self._session_modes

    def _create_background(self):
        self._background = NotifyingBackgroundComponent(
            name="Background",
            is_enabled=False,
            add_nop_listeners=True,
            layer=Layer(
                drums_mode_button="drums_mode_button",
                keys_mode_button="keys_mode_button",
                user_mode_button="user_mode_button",
            ),
        )
        self._background.set_enabled(True)
        self.__on_background_control_value.subject = self._background

    @listens("selected_mode")
    def __on_session_mode_changed(self, _):
        self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_background_control_value(self, control, value):
        if value and "Mode" in control.name:
            self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_layout_switch_value(self, value):
        self._last_layout_byte = value
