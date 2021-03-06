from ableton.v2.base import listens
from ableton.v2.control_surface import Layer, merge_skins
from ableton.v2.control_surface.components import SessionOverviewComponent
from ableton.v2.control_surface.components.session_ring import SessionRingComponent
from ableton.v2.control_surface.mode import AddLayerMode
from ableton.v2.control_surface.skin import Skin
from Launchpad_Mini_MK3 import sysex_ids as ids
from Launchpad_Mini_MK3.elements import Elements
from Launchpad_Mini_MK3.notifying_background import NotifyingBackgroundComponent
from Launchpad_Mini_MK3.skin import skin as default_mk3_skin
from novation import sysex
from novation.colors import CLIP_COLOR_TABLE, RGB_COLOR_TABLE, Rgb
from novation.launchpad_elements import SESSION_WIDTH
from novation.session_modes import SessionModesComponent
from novation.session_navigation import SessionNavigationComponent
from novation.skin import Colors

from .novation_base_augmented import NovationBaseAugmented


class ColorsAugmented(Colors):
    class Mixer(Colors.Mixer):
        SendControls = Rgb.PURPLE


augmented_skin = merge_skins(*(default_mk3_skin, Skin(ColorsAugmented)))


class Launchpad_Mini_MK3_Augmented(NovationBaseAugmented):

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
        self._create_sends_mode()
        self.__on_layout_switch_value.subject = self._elements.layout_switch

    def _create_session(self):
        self._session_ring = SessionRingComponent(
            name="Session_Ring",
            is_enabled=False,
            num_tracks=SESSION_WIDTH,
            num_scenes=self.session_height,
            tracks_to_use=lambda: tuple(self.song.visible_tracks)
            + tuple(self.song.return_tracks)
            + (self.song.master_track,),
        )
        self._session = self.session_class(
            name="Session",
            is_enabled=False,
            session_ring=self._session_ring,
            layer=self._create_session_layer(),
        )
        self._session.set_rgb_mode(CLIP_COLOR_TABLE, RGB_COLOR_TABLE)
        self._session.set_enabled(True)
        self._session_navigation = SessionNavigationComponent(
            name="Session_Navigation",
            is_enabled=False,
            session_ring=self._session_ring,
            layer=self._create_session_navigation_layer(),
        )
        self._session_navigation.set_enabled(True)

    def _create_sends_mode(self):
        self._session_overview = SessionOverviewComponent(
            name="Session_Overview",
            is_enabled=False,
            session_ring=self._session_ring,
            enable_skinning=True,
        )
        self._sends_mode = SessionModesComponent(
            name="Session_Modes",
            is_enabled=False,
            layer=Layer(
                cycle_mode_button="session_mode_button",
                mode_button_color_control="session_button_color_element",
            ),
        )
        self._sends_mode.add_mode(
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
            ),
        )
        row_8 = self._elements.clip_launch_matrix.submatrix[:, 7:8]
        self._sends_mode.add_mode(
            "sends",
            AddLayerMode(
                self._mixer,
                Layer(
                    send_controls=self._elements.clip_launch_matrix,
                    mute_buttons=row_8,
                ),
            ),
        )
        self._sends_mode.selected_mode = "sends"
        self._sends_mode.set_enabled(True)
        self.__on_sends_mode_changed.subject = self._sends_mode

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
    def __on_sends_mode_changed(self, _):
        self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_background_control_value(self, control, value):
        if value and "Mode" in control.name:
            self._elements.layout_switch.enquire_value()

    @listens("value")
    def __on_layout_switch_value(self, value):
        self._last_layout_byte = value
