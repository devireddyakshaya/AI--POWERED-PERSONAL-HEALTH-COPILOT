import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Activity,
  Accessibility,
  CheckCircle2,
  Globe,
  Mic,
  PlayCircle,
  Search,
  User,
  Users,
  Volume2
} from 'lucide-react';
import { LANGUAGES, LanguageCode, SupportLevel, t } from '../i18n/translations';
import { VoiceType } from '../types';
import { useAppSettings } from '../context/AppSettings';
import { useSpeech } from '../hooks/useSpeech';

interface OnboardingFlowProps {
  onComplete: (language: LanguageCode, voiceType: VoiceType) => void;
}

type Step = 'welcome' | 'language' | 'voice';

const LANGUAGE_KEYWORDS: Record<LanguageCode, string[]> = {
  en: ['english', 'inglish', 'angrezi', 'इंग्लिश', 'ఆంగ్ల'],
  te: ['telugu', 'telgu', 'తెలుగు'],
  hi: ['hindi', 'हिन्दी', 'हिंदी'],
  ta: ['tamil', 'தமிழ்'],
  kn: ['kannada', 'kannad', 'ಕನ್ನಡ'],
  ml: ['malayalam', 'മലയാളം'],
  bn: ['bengali', 'bangla', 'বাংলা'],
  mr: ['marathi', 'मराठी'],
  gu: ['gujarati', 'ગુજરાતી'],
  pa: ['punjabi', 'panjabi', 'ਪੰਜਾਬੀ'],
  ur: ['urdu', 'اردو'],
  or: ['odia', 'oriya', 'ଓଡ଼ିଆ']
};

const FEMALE_KEYWORDS = ['female', 'woman', 'lady', 'girl', 'స్త్రీ', 'ఆడ', 'महिला', 'औरत', 'लड़की', 'பெண்', 'ಮಹಿಳೆ', 'സ്ത്രീ'];
const MALE_KEYWORDS = ['male', 'man', 'boy', 'పురుష', 'पुरुष', 'मर्द', 'लड़का', 'ஆண்', 'ಪುರುಷ', 'പുരുഷ'];
const SYSTEM_KEYWORDS = ['default', 'system', 'device', 'సాధారణ', 'डिफ़ॉल्ट', 'இயல்புநிலை', 'ಡಿಫಾಲ್ಟ್'];

const SUPPORT_STYLES: Record<SupportLevel, string> = {
  complete: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  partial: 'bg-amber-100 text-amber-800 border-amber-200',
  unavailable: 'bg-slate-100 text-slate-600 border-slate-200'
};

const supportLabelKey: Record<SupportLevel, 'support_complete' | 'support_partial' | 'support_unavailable'> = {
  complete: 'support_complete',
  partial: 'support_partial',
  unavailable: 'support_unavailable'
};

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [step, setStep] = useState<Step>('welcome');
  const [language, setLanguage] = useState<LanguageCode>('en');
  const [voiceType, setVoiceType] = useState<VoiceType>('system');
  const [search, setSearch] = useState('');
  const [showA11y, setShowA11y] = useState(false);

  const settings = useAppSettings();
  const speech = useSpeech(language, voiceType);
  const stepSpokenRef = useRef<string>('');

  const matchLanguage = (text: string): LanguageCode | null => {
    const value = text.toLowerCase();
    for (const code of Object.keys(LANGUAGE_KEYWORDS) as LanguageCode[]) {
      if (LANGUAGE_KEYWORDS[code].some((kw) => value.includes(kw.toLowerCase()))) return code;
    }
    return null;
  };

  const matchVoice = (text: string): VoiceType | null => {
    const value = text.toLowerCase();
    if (FEMALE_KEYWORDS.some((kw) => value.includes(kw.toLowerCase()))) return 'female';
    if (MALE_KEYWORDS.some((kw) => value.includes(kw.toLowerCase()))) return 'male';
    if (SYSTEM_KEYWORDS.some((kw) => value.includes(kw.toLowerCase()))) return 'system';
    return null;
  };

  const listenFor = useCallback(
    (currentStep: 'language' | 'voice', currentLang: LanguageCode) => {
      if (!speech.sttSupported) return;
      speech.listen((transcript) => {
        if (currentStep === 'language') {
          const code = matchLanguage(transcript);
          if (code) {
            stepSpokenRef.current = '';
            setLanguage(code);
            setStep('voice');
          } else {
            speech.speak(t(currentLang, 'listen_failed'), {
              langCode: currentLang,
              onEnd: () => listenFor('language', currentLang)
            });
          }
        } else {
          const v = matchVoice(transcript);
          if (v) {
            setVoiceType(v);
            speech.speak(t(currentLang, 'voice_saved'), {
              langCode: currentLang,
              onEnd: () => onComplete(currentLang, v)
            });
          } else {
            speech.speak(t(currentLang, 'listen_failed'), {
              langCode: currentLang,
              onEnd: () => listenFor('voice', currentLang)
            });
          }
        }
      });
    },
    [speech, onComplete]
  );

  useEffect(() => {
    if (step === 'welcome') return;
    if (stepSpokenRef.current === step) return;
    stepSpokenRef.current = step;

    const prompt =
      step === 'language'
        ? `${t(language, 'choose_language_title')}. ${t(language, 'choose_language_sub')}`
        : `${t(language, 'voice_select_title')}. ${t(language, 'voice_select_sub')}`;

    speech.speak(prompt, {
      langCode: language,
      onEnd: () => listenFor(step as 'language' | 'voice', language)
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step, language]);

  const goToLanguage = () => {
    stepSpokenRef.current = '';
    setStep('language');
    speech.speak(`${t(language, 'onboarding_welcome')}. ${t(language, 'choose_language_title')}`, {
      langCode: language,
      onEnd: () => listenFor('language', language)
    });
  };

  const goToVoice = (code?: LanguageCode) => {
    stepSpokenRef.current = '';
    if (code) setLanguage(code);
    setStep('voice');
  };

  const finish = (value: VoiceType, lang: LanguageCode) => {
    setVoiceType(value);
    settings.update({ voiceType: value });
    speech.speak(t(lang, 'voice_saved'), {
      langCode: lang,
      onEnd: () => onComplete(lang, value)
    });
  };

  const tryDemo = () => {
    settings.update({ voiceType: 'system' });
    onComplete('en', 'system');
  };

  const filteredLanguages = LANGUAGES.filter((lang) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      lang.label.toLowerCase().includes(q) ||
      lang.nativeLabel.toLowerCase().includes(q) ||
      lang.code.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-blue-700 via-blue-800 to-slate-900 px-4 py-10">
      <div
        role="dialog"
        aria-modal="true"
        aria-label="MediMitra onboarding"
        className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="bg-slate-900 text-white px-6 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-500 to-cyan-500 flex items-center justify-center">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="text-base font-extrabold leading-tight">{t(language, 'app_name')}</div>
              <div className="text-[11px] text-slate-300">{t(language, 'tagline')}</div>
            </div>
          </div>
          <span className="inline-flex items-center space-x-1.5 text-[11px] font-semibold bg-blue-900/70 text-blue-200 border border-blue-700/60 rounded-full px-2.5 py-1">
            <Accessibility className="w-3.5 h-3.5" />
            <span>Voice First</span>
          </span>
        </div>

        <div className="p-6 sm:p-9">
          {step === 'welcome' && (
            <div className="space-y-7">
              <div className="text-center space-y-3">
                <div className="w-20 h-20 mx-auto rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center">
                  <Volume2 className="w-10 h-10 text-blue-700" />
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  {t(language, 'welcome_headline')}
                </h1>
                <p className="text-sm text-slate-500 max-w-xl mx-auto">{t(language, 'welcome_sub')}</p>
              </div>

              <button
                onClick={goToLanguage}
                className="w-full inline-flex items-center justify-center space-x-2 px-8 py-4 rounded-2xl bg-blue-700 hover:bg-blue-800 text-white text-base font-bold shadow-lg shadow-blue-700/20 transition-all a11y-tap-target"
              >
                <Mic className="w-5 h-5" />
                <span>{t(language, 'welcome_start')}</span>
              </button>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <WelcomeOption
                  icon={<Globe className="w-5 h-5" />}
                  label={t(language, 'welcome_select_language')}
                  onClick={goToLanguage}
                />
                <WelcomeOption
                  icon={<User className="w-5 h-5" />}
                  label={t(language, 'welcome_voice_assistant')}
                  onClick={() => goToVoice()}
                />
                <WelcomeOption
                  icon={<Accessibility className="w-5 h-5" />}
                  label={t(language, 'welcome_accessibility')}
                  onClick={() => setShowA11y((v) => !v)}
                />
                <WelcomeOption
                  icon={<PlayCircle className="w-5 h-5" />}
                  label={t(language, 'welcome_try_demo')}
                  onClick={tryDemo}
                />
              </div>

              {showA11y && <AccessibilityPanelInline />}

              <p className="text-[11px] text-slate-400 text-center">{t(language, 'welcome_footer_note')}</p>
            </div>
          )}

          {step === 'language' && (
            <div className="space-y-5">
              <div className="text-center">
                <Globe className="w-9 h-9 text-blue-700 mx-auto mb-2" />
                <h2 className="text-2xl font-extrabold text-slate-900">{t(language, 'choose_language_title')}</h2>
                <p className="text-sm text-slate-500 mt-1">{t(language, 'choose_language_sub')}</p>
              </div>

              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t(language, 'search_language')}
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-72 overflow-y-auto pr-1">
                {filteredLanguages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => goToVoice(lang.code)}
                    aria-label={`${lang.label} - ${t(language, supportLabelKey[lang.support])}`}
                    className={`p-3 rounded-2xl border-2 text-center transition-all a11y-tap-target ${
                      language === lang.code
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="text-base font-extrabold text-slate-900">{lang.nativeLabel}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">{lang.label}</div>
                    <span
                      className={`inline-block mt-1.5 text-[9px] font-bold px-1.5 py-0.5 rounded border ${SUPPORT_STYLES[lang.support]}`}
                    >
                      {t(language, supportLabelKey[lang.support])}
                    </span>
                  </button>
                ))}
                {filteredLanguages.length === 0 && (
                  <p className="col-span-full text-center text-sm text-slate-500 py-6">
                    {t(language, 'no_language_found')}
                  </p>
                )}
              </div>

              <p className="text-[11px] text-slate-400 text-center">{t(language, 'language_support_note')}</p>
            </div>
          )}

          {step === 'voice' && (
            <div className="space-y-6">
              <div className="text-center">
                <User className="w-9 h-9 text-blue-700 mx-auto mb-2" />
                <h2 className="text-2xl font-extrabold text-slate-900">{t(language, 'voice_select_title')}</h2>
                <p className="text-sm text-slate-500 mt-1">{t(language, 'voice_select_sub')}</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {(['female', 'male', 'system'] as VoiceType[]).map((value) => (
                  <button
                    key={value}
                    onClick={() => finish(value, language)}
                    className={`p-5 rounded-2xl border-2 font-bold text-sm transition-all flex flex-col items-center gap-2 a11y-tap-target ${
                      voiceType === value
                        ? 'border-blue-600 bg-blue-50 text-blue-900'
                        : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50 text-slate-800'
                    }`}
                  >
                    {value === 'system' ? <Users className="w-6 h-6" /> : <User className="w-6 h-6" />}
                    <span>
                      {t(
                        language,
                        value === 'female' ? 'voice_type_female' : value === 'male' ? 'voice_type_male' : 'voice_type_system'
                      )}
                    </span>
                  </button>
                ))}
              </div>

              <button
                onClick={() => speech.speak(t(language, 'assistant_greeting'), { langCode: language })}
                className="mx-auto flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold"
              >
                <Volume2 className="w-4 h-4 text-blue-600" />
                <span>{t(language, 'test_voice')}</span>
              </button>

              <p className="text-[11px] text-slate-400 text-center">{t(language, 'voice_unavailable_note')}</p>
            </div>
          )}

          {/* Voice status bar */}
          {step !== 'welcome' && (
            <div className="mt-7 flex items-center justify-between rounded-2xl bg-slate-50 border border-slate-200 px-4 py-3">
              <span className="flex items-center space-x-2 text-xs font-semibold text-slate-600">
                {speech.isListening ? (
                  <>
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
                    <span>{t(language, 'listening')}</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-blue-600" />
                    <span>{speech.isSpeaking ? t(language, 'voice_guide') : t(language, 'speak_now')}</span>
                  </>
                )}
              </span>
              {speech.sttSupported && (
                <button
                  onClick={() => listenFor(step as 'language' | 'voice', language)}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-700 text-white text-xs font-bold"
                >
                  <Mic className="w-3.5 h-3.5" />
                  <span>{t(language, 'speak_now')}</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const WelcomeOption: React.FC<{ icon: React.ReactNode; label: string; onClick: () => void }> = ({
  icon,
  label,
  onClick
}) => (
  <button
    onClick={onClick}
    className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/60 text-slate-700 transition-all a11y-tap-target"
  >
    <span className="text-blue-700">{icon}</span>
    <span className="text-[11px] font-bold text-center leading-tight">{label}</span>
  </button>
);

const AccessibilityPanelInline: React.FC = () => {
  const settings = useAppSettings();
  const rows: { key: keyof ReturnType<typeof useAppSettings>; label: string; desc: string }[] = [];
  void rows;
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 space-y-3">
      <div className="text-xs font-bold text-slate-700">Accessibility Settings</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <ToggleRow
          label="Simple Mode"
          desc="Bigger buttons, fewer options."
          checked={settings.simpleMode}
          onChange={(v) => settings.update({ simpleMode: v })}
        />
        <ToggleRow
          label="High contrast"
          desc="Stronger colours for low vision."
          checked={settings.highContrast}
          onChange={(v) => settings.update({ highContrast: v })}
        />
        <ToggleRow
          label="Larger text"
          desc="Increase text size across the app."
          checked={settings.largeText}
          onChange={(v) => settings.update({ largeText: v })}
        />
        <ToggleRow
          label="Reduce motion"
          desc="Turn off animations."
          checked={settings.reduceMotion}
          onChange={(v) => settings.update({ reduceMotion: v })}
        />
      </div>
    </div>
  );
};

const ToggleRow: React.FC<{
  label: string;
  desc: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}> = ({ label, desc, checked, onChange }) => (
  <button
    onClick={() => onChange(!checked)}
    role="switch"
    aria-checked={checked}
    className={`flex items-center justify-between gap-3 p-3 rounded-xl border text-left transition-all ${
      checked ? 'border-blue-400 bg-blue-50' : 'border-slate-200 bg-white'
    }`}
  >
    <span>
      <span className="block text-xs font-bold text-slate-800">{label}</span>
      <span className="block text-[10px] text-slate-500">{desc}</span>
    </span>
    <span
      className={`w-9 h-5 rounded-full shrink-0 flex items-center px-0.5 transition-colors ${
        checked ? 'bg-blue-600 justify-end' : 'bg-slate-300 justify-start'
      }`}
    >
      <span className="w-4 h-4 rounded-full bg-white shadow" />
    </span>
  </button>
);
