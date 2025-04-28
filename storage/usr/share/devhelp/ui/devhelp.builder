<?xml version="1.0"?>
<!--*- mode: xml -*-->
<interface>
  <object class="GtkDialog" id="preferences_dialog">
    <property name="border_width">5</property>
    <property name="title" translatable="yes">Preferences</property>
    <property name="type">GTK_WINDOW_TOPLEVEL</property>
    <property name="window_position">GTK_WIN_POS_NONE</property>
    <property name="modal">False</property>
    <property name="resizable">False</property>
    <property name="destroy_with_parent">False</property>
    <property name="decorated">True</property>
    <property name="skip_taskbar_hint">False</property>
    <property name="skip_pager_hint">False</property>
    <property name="type_hint">GDK_WINDOW_TYPE_HINT_DIALOG</property>
    <property name="gravity">GDK_GRAVITY_NORTH_WEST</property>
    <property name="focus_on_map">True</property>
    <property name="urgency_hint">False</property>
    <property name="has_separator">False</property>
    <child internal-child="vbox">
      <object class="GtkVBox" id="dialog-vbox1">
        <property name="visible">True</property>
        <property name="homogeneous">False</property>
        <property name="spacing">2</property>
        <child internal-child="action_area">
          <object class="GtkHButtonBox" id="dialog-action_area1">
            <property name="visible">True</property>
            <property name="layout_style">GTK_BUTTONBOX_END</property>
            <child>
              <object class="GtkButton" id="close_button">
                <property name="visible">True</property>
                <property name="can_default">True</property>
                <property name="can_focus">True</property>
                <property name="label">gtk-close</property>
                <property name="use_stock">True</property>
                <property name="relief">GTK_RELIEF_NORMAL</property>
                <property name="focus_on_click">True</property>
              </object>
            </child>
          </object>
          <packing>
            <property name="padding">0</property>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="pack_type">GTK_PACK_END</property>
          </packing>
        </child>
        <child>
          <object class="GtkVBox" id="outer_vbox">
            <property name="border_width">5</property>
            <property name="visible">True</property>
            <property name="homogeneous">False</property>
            <property name="spacing">18</property>
            <child>
              <object class="GtkVBox" id="font_vbox">
                <property name="visible">True</property>
                <property name="homogeneous">False</property>
                <property name="spacing">6</property>
                <child>
                  <object class="GtkLabel" id="label6">
                    <property name="visible">True</property>
                    <property name="label" translatable="yes">&lt;b&gt;Fonts&lt;/b&gt;</property>
                    <property name="use_underline">False</property>
                    <property name="use_markup">True</property>
                    <property name="justify">GTK_JUSTIFY_LEFT</property>
                    <property name="wrap">False</property>
                    <property name="selectable">False</property>
                    <property name="xalign">0</property>
                    <property name="yalign">0.5</property>
                    <property name="xpad">0</property>
                    <property name="ypad">0</property>
                    <property name="ellipsize">PANGO_ELLIPSIZE_NONE</property>
                    <property name="width_chars">-1</property>
                    <property name="single_line_mode">False</property>
                    <property name="angle">0</property>
                  </object>
                  <packing>
                    <property name="padding">0</property>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                  </packing>
                </child>
                <child>
                  <object class="GtkAlignment" id="alignment1">
                    <property name="visible">True</property>
                    <property name="xalign">0.5</property>
                    <property name="yalign">0.5</property>
                    <property name="xscale">1</property>
                    <property name="yscale">1</property>
                    <property name="top_padding">0</property>
                    <property name="bottom_padding">0</property>
                    <property name="left_padding">12</property>
                    <property name="right_padding">0</property>
                    <child>
                      <object class="GtkVBox" id="vbox3">
                        <property name="visible">True</property>
                        <property name="homogeneous">False</property>
                        <property name="spacing">6</property>
                        <child>
                          <object class="GtkCheckButton" id="system_fonts_button">
                            <property name="visible">True</property>
                            <property name="can_focus">True</property>
                            <property name="label" translatable="yes">_Use system fonts</property>
                            <property name="use_underline">True</property>
                            <property name="relief">GTK_RELIEF_NORMAL</property>
                            <property name="focus_on_click">True</property>
                            <property name="active">True</property>
                            <property name="inconsistent">False</property>
                            <property name="draw_indicator">True</property>
                          </object>
                          <packing>
                            <property name="padding">0</property>
                            <property name="expand">False</property>
                            <property name="fill">False</property>
                          </packing>
                        </child>
                        <child>
                          <object class="GtkTable" id="fonts_table">
                            <property name="visible">True</property>
                            <property name="sensitive">False</property>
                            <property name="n_rows">2</property>
                            <property name="n_columns">2</property>
                            <property name="homogeneous">False</property>
                            <property name="row_spacing">6</property>
                            <property name="column_spacing">6</property>
                            <child>
                              <object class="GtkLabel" id="label8">
                                <property name="visible">True</property>
                                <property name="label" translatable="yes">_Variable width: </property>
                                <property name="use_underline">True</property>
                                <property name="use_markup">False</property>
                                <property name="justify">GTK_JUSTIFY_LEFT</property>
                                <property name="wrap">False</property>
                                <property name="selectable">False</property>
                                <property name="xalign">0</property>
                                <property name="yalign">0.5</property>
                                <property name="xpad">0</property>
                                <property name="ypad">0</property>
                                <property name="mnemonic_widget">variable_font_button</property>
                                <property name="ellipsize">PANGO_ELLIPSIZE_NONE</property>
                                <property name="width_chars">-1</property>
                                <property name="single_line_mode">False</property>
                                <property name="angle">0</property>
                              </object>
                              <packing>
                                <property name="left_attach">0</property>
                                <property name="right_attach">1</property>
                                <property name="top_attach">0</property>
                                <property name="bottom_attach">1</property>
                                <property name="x_options">fill</property>
                                <property name="y_options"/>
                              </packing>
                            </child>
                            <child>
                              <object class="GtkLabel" id="label9">
                                <property name="visible">True</property>
                                <property name="label" translatable="yes">_Fixed width:</property>
                                <property name="use_underline">True</property>
                                <property name="use_markup">False</property>
                                <property name="justify">GTK_JUSTIFY_LEFT</property>
                                <property name="wrap">False</property>
                                <property name="selectable">False</property>
                                <property name="xalign">0</property>
                                <property name="yalign">0.5</property>
                                <property name="xpad">0</property>
                                <property name="ypad">0</property>
                                <property name="mnemonic_widget">fixed_font_button</property>
                                <property name="ellipsize">PANGO_ELLIPSIZE_NONE</property>
                                <property name="width_chars">-1</property>
                                <property name="single_line_mode">False</property>
                                <property name="angle">0</property>
                              </object>
                              <packing>
                                <property name="left_attach">0</property>
                                <property name="right_attach">1</property>
                                <property name="top_attach">1</property>
                                <property name="bottom_attach">2</property>
                                <property name="x_options">fill</property>
                                <property name="y_options"/>
                              </packing>
                            </child>
                            <child>
                              <object class="GtkFontButton" id="variable_font_button">
                                <property name="visible">True</property>
                                <property name="can_focus">True</property>
                                <property name="show_style">True</property>
                                <property name="show_size">True</property>
                                <property name="use_font">True</property>
                                <property name="use_size">False</property>
                                <property name="focus_on_click">True</property>
                              </object>
                              <packing>
                                <property name="left_attach">1</property>
                                <property name="right_attach">2</property>
                                <property name="top_attach">0</property>
                                <property name="bottom_attach">1</property>
                                <property name="y_options"/>
                              </packing>
                            </child>
                            <child>
                              <object class="GtkFontButton" id="fixed_font_button">
                                <property name="visible">True</property>
                                <property name="can_focus">True</property>
                                <property name="show_style">True</property>
                                <property name="show_size">True</property>
                                <property name="use_font">True</property>
                                <property name="use_size">False</property>
                                <property name="focus_on_click">True</property>
                              </object>
                              <packing>
                                <property name="left_attach">1</property>
                                <property name="right_attach">2</property>
                                <property name="top_attach">1</property>
                                <property name="bottom_attach">2</property>
                                <property name="y_options"/>
                              </packing>
                            </child>
                          </object>
                          <packing>
                            <property name="padding">0</property>
                            <property name="expand">True</property>
                            <property name="fill">True</property>
                          </packing>
                        </child>
                      </object>
                    </child>
                  </object>
                  <packing>
                    <property name="padding">0</property>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                  </packing>
                </child>
              </object>
              <packing>
                <property name="padding">0</property>
                <property name="expand">False</property>
                <property name="fill">False</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="padding">0</property>
            <property name="expand">True</property>
            <property name="fill">True</property>
          </packing>
        </child>
      </object>
    </child>
    <action-widgets>
      <action-widget response="-7">close_button</action-widget>
    </action-widgets>
  </object>
</interface>
