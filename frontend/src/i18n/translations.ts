/**
 * Backwards-compatible shim.
 *
 * Locale files now live under `src/locales/`. Existing imports such as
 * `from '../i18n/translations'` continue to work through this re-export.
 */
export {
  LANGUAGES,
  TRANSLATIONS,
  getLanguage,
  t,
  isComplete,
  ENGLISH,
} from '../locales';

export type {
  LanguageCode,
  LanguageOption,
  TranslationKey,
  Dict,
  PartialDict,
  SupportLevel,
} from '../locales/types';
