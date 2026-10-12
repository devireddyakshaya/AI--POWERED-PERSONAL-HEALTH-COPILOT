/**
 * MediMitra AI — i18n shared types.
 *
 * Interface translations live in one file per language under `src/locales/`.
 * English is the reference dictionary and defines the full set of keys. Other
 * languages are stored as partial dictionaries and gracefully fall back to
 * English for any key they do not yet translate, so a missing string never
 * breaks the UI.
 */

export type LanguageCode =
  | 'en'
  | 'te'
  | 'hi'
  | 'ta'
  | 'kn'
  | 'ml'
  | 'bn'
  | 'mr'
  | 'gu'
  | 'pa'
  | 'ur'
  | 'or';

/**
 * How complete a language's coverage is. We never claim a language is fully
 * supported unless it truly is. `complete` = all interface + medical strings,
 * `partial` = interface strings mostly present but explanations may fall back
 * to English, `unavailable` = listed for reference only.
 */
export type SupportLevel = 'complete' | 'partial' | 'unavailable';

export interface LanguageOption {
  code: LanguageCode;
  /** English name, used for search. */
  label: string;
  /** Name written in the language itself. */
  nativeLabel: string;
  /** BCP-47 tag used for speech synthesis / recognition. */
  speechCode: string;
  support: SupportLevel;
}

export type TranslationKey =
  // Brand & general
  | 'app_name'
  | 'tagline'
  | 'on'
  | 'off'
  // Welcome / get started
  | 'welcome_headline'
  | 'welcome_sub'
  | 'welcome_start'
  | 'welcome_select_language'
  | 'welcome_voice_assistant'
  | 'welcome_accessibility'
  | 'welcome_try_demo'
  | 'welcome_footer_note'
  | 'onboarding_welcome'
  // Language selection
  | 'choose_language_title'
  | 'choose_language_sub'
  | 'search_language'
  | 'no_language_found'
  | 'support_complete'
  | 'support_partial'
  | 'support_unavailable'
  | 'language_support_note'
  | 'confirm_language'
  | 'language_saved'
  // Voice selection
  | 'choose_gender_title'
  | 'choose_gender_sub'
  | 'voice_select_title'
  | 'voice_select_sub'
  | 'voice_type_female'
  | 'voice_type_male'
  | 'voice_type_system'
  | 'voice_saved'
  | 'test_voice'
  | 'voice_unavailable_note'
  | 'voice_pick_help'
  | 'female'
  | 'male'
  | 'gender_saved'
  // Accessibility settings
  | 'accessibility_title'
  | 'accessibility_sub'
  | 'simple_mode'
  | 'simple_mode_desc'
  | 'high_contrast'
  | 'high_contrast_desc'
  | 'large_text'
  | 'large_text_desc'
  | 'reduce_motion'
  | 'reduce_motion_desc'
  | 'spoken_labels'
  | 'spoken_labels_desc'
  | 'reset_settings'
  | 'settings_saved'
  | 'read_this_page'
  | 'text_size'
  // Voice guide / assistant
  | 'voice_guide'
  | 'voice_guide_sub'
  | 'assistant_name'
  | 'assistant_greeting'
  | 'assistant_help'
  | 'voice_on'
  | 'voice_off'
  | 'stop'
  | 'stop_speaking'
  | 'repeat'
  | 'read_report'
  | 'no_report'
  | 'navigate'
  | 'tap_to_start'
  | 'listening'
  | 'speak_now'
  | 'continue'
  | 'redo_setup'
  | 'start'
  // Navigation
  | 'nav_dashboard'
  | 'nav_upload'
  | 'nav_reports'
  | 'nav_explainer'
  | 'nav_summary'
  | 'nav_ask'
  | 'nav_voice'
  | 'nav_timeline'
  | 'nav_trends'
  | 'nav_doctor'
  | 'nav_medications'
  | 'nav_accessibility'
  | 'nav_privacy'
  | 'nav_about'
  | 'nav_comparison'
  // Dashboard cards
  | 'dash_greeting'
  | 'card_upload'
  | 'card_upload_desc'
  | 'card_reports'
  | 'card_reports_desc'
  | 'card_summary'
  | 'card_summary_desc'
  | 'card_ask'
  | 'card_ask_desc'
  | 'card_voice'
  | 'card_voice_desc'
  | 'card_timeline'
  | 'card_timeline_desc'
  | 'card_trends'
  | 'card_trends_desc'
  | 'card_medicines'
  | 'card_medicines_desc'
  | 'card_accessibility'
  | 'card_accessibility_desc'
  | 'card_privacy'
  | 'card_privacy_desc'
  // Upload
  | 'upload_title'
  | 'upload_sub'
  // Reports
  | 'my_reports_title'
  | 'my_reports_sub'
  // Health trends
  | 'trends_title'
  | 'trends_sub'
  | 'trends_no_data'
  | 'trends_pick_test'
  | 'trends_points'
  | 'trends_unit_label'
  | 'trends_reference'
  | 'trends_listen'
  | 'trends_insufficient'
  | 'trends_single_point'
  // Ask MediMitra
  | 'ask_page_title'
  | 'ask_page_sub'
  | 'ask_example_label'
  | 'ask_clear_chat'
  | 'ask_source_report'
  // About
  | 'about_title'
  | 'about_tagline'
  | 'about_mission'
  | 'about_features_title'
  | 'about_stack_title'
  | 'about_disclaimer_title'
  | 'about_demo_note'
  | 'about_tech_ocr'
  | 'about_tech_ai'
  | 'about_tech_voice'
  | 'about_tech_privacy'
  // Errors / status
  | 'listen_failed'
  | 'unsupported_voice'
  | 'thinking'
  | 'assistant_speaking'
  | 'ai_thinking'
  | 'you_said'
  | 'ask_placeholder'
  | 'ask_send'
  | 'error_no_speech'
  | 'error_mic_permission'
  | 'error_network'
  | 'error_generic';

export type Dict = Record<TranslationKey, string>;

/** A locale may translate only some keys; missing ones fall back to English. */
export type PartialDict = Partial<Dict>;
