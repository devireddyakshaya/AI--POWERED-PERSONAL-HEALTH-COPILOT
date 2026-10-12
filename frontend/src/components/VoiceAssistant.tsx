import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  X,
  UploadCloud,
  FileText,
  Clock,
  Pill,
  GitCompare,
  Stethoscope,
  ShieldCheck,
  Activity,
  Settings,
  Send,
  Loader2,
  Sparkles,
  Trash2
} from 'lucide-react';
import { LanguageCode, TranslationKey, getLanguage, t } from '../i18n/translations';
import { DocumentDetail } from '../types';
import { useSpeech } from '../hooks/useSpeech';
import { askVoiceAssistant, fetchLocalizedExplanation } from '../services/api';

interface VoiceAssistantProps {
  language: LanguageCode;
  onNavigate: (tab: string) => void;
  activeDocument: DocumentDetail | null;
  onOpenSetup: () => void;
}

type Status = 'idle' | 'listening' | 'speaking' | 'thinking';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  text: string;
}

const KEYWORDS = {
  stop: ['stop', 'quiet', 'silence', 'ఆపు', 'रुको', 'चुप', 'நிறுத்து', 'ನಿಲ್ಲಿಸು', 'നിർത്തുക'],
  changeLanguage: ['change language', 'change the language', 'భాష మార్చు', 'भाषा बदलो', 'மொழி மாற்று', 'ಭಾಷೆ ಬದಲಾಯಿಸು', 'ഭാഷ മാറ്റുക'],
  upload: ['upload', 'add report', 'add a report', 'new report', 'అప్‌లోడ్', 'अपलोड', 'पर्चा', 'பதிவேற்ற', 'அப்லோட', 'ಅಪ್‌ಲೋಡ್', 'അപ്‌ലോഡ്'],
  read: ['read my report', 'read the report', 'explain my report', 'my report', 'చదువు', 'వివరణ', 'చెప్పు', 'पढ़', 'पढो', 'व्याख्या', 'வாசி', 'விளக்க', 'ವಿವರಣೆ', 'ಓದು', 'വായിക്ക', 'വിശദീകര'],
  timeline: ['timeline', 'history', 'టైమ్‌లైన్', 'चक्र', 'टाइमलाइन', 'டைம்லைன்', 'ಟೈಮ್‌ಲೈನ್', 'ടൈംലൈൻ'],
  medicines: ['show my medicine', 'show my medication', 'show medicines', 'my medicines', 'my medication', 'దవా', 'दवा', 'दवाई', 'மருந்து', 'ಔಷಧ', 'ಮಾತ್ರೆ', 'മരുന്ന'],
  comparison: ['compare', 'comparison', 'change detector', 'trend', 'మార్పు', 'बदलाव', 'மாற்ற', 'ஒப்பிடு', 'ಬದಲಾವಣೆ', 'ഒപ്പിട'],
  doctor: ['doctor prep', 'doctor questions', 'ask doctor', 'డాక్టర్ ప్రశ్న', 'डॉक्टर', 'மருத்துவ', 'ವೈದ್ಯ', 'ഡോക്ട'],
  dashboard: ['dashboard', 'home', 'overview', 'డ్యాష్‌బోర్డ్', 'होम', 'मुख्य', 'முகப்ப', 'ಮುಖಪುಟ', 'ഹോം'],
  privacy: ['privacy', 'fhir', 'vault', 'గోప్యత', 'गोपनीयता', 'தனியுரிமை', 'ಗೌಪ್ಯತೆ', 'സ്വകാര്യത']
};

const containsAny = (text: string, list: string[]): boolean =>
  list.some((kw) => text.includes(kw.toLowerCase()));

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({
  language,
  onNavigate,
  activeDocument,
  onOpenSetup
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [handsFree, setHandsFree] = useState(false);
  const [status, setStatus] = useState<Status>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState('');
  const speech = useSpeech(language);
  const documentRef = useRef<DocumentDetail | null>(activeDocument);
  const handsFreeRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const idRef = useRef(0);

  useEffect(() => {
    documentRef.current = activeDocument;
  }, [activeDocument]);

  useEffect(() => {
    handsFreeRef.current = handsFree;
  }, [handsFree]);

  const nextId = () => {
    idRef.current += 1;
    return idRef.current;
  };

  const pushMessage = useCallback((role: ChatMessage['role'], text: string) => {
    setMessages((prev) => [...prev, { id: nextId(), role, text }]);
  }, []);

  // Keep the newest message in view as the conversation grows.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, status]);

  const speakAnswer = useCallback(
    (text: string) => {
      const clean = (text || '').trim();
      if (!clean) return;
      pushMessage('assistant', clean);
      setStatus('speaking');
      speech.speak(clean, { onEnd: () => setStatus('idle') });
    },
    [pushMessage, speech]
  );

  const stop = useCallback(() => {
    speech.stopSpeaking();
    speech.stopListening();
    setStatus('idle');
  }, [speech]);

  const readReport = useCallback(async () => {
    const doc = documentRef.current;
    if (!doc) {
      speakAnswer(t(language, 'no_report'));
      return;
    }
    setStatus('thinking');
    let text = '';
    try {
      const localized = await fetchLocalizedExplanation(doc.id, language);
      if (localized?.summary) text = localized.summary;
    } catch {
      /* ignore */
    }
    if (!text) {
      const summary = doc.summary;
      if (language === 'te' && summary?.telugu_summary) text = summary.telugu_summary;
      else if (summary?.english_summary) text = summary.english_summary;
    }
    speakAnswer(text || t(language, 'no_report'));
  }, [language, speakAnswer]);

  const navigateAndSpeak = useCallback(
    (tab: string, labelKey: Parameters<typeof t>[1]) => {
      onNavigate(tab);
      speakAnswer(`${t(language, 'navigate')} ${t(language, labelKey)}`);
    },
    [language, onNavigate, speakAnswer]
  );

  const ask = useCallback(
    async (raw: string) => {
      const text = raw.trim();
      if (!text) return;
      pushMessage('user', text);
      setStatus('thinking');
      speech.stopListening();
      try {
        const res = await askVoiceAssistant(text, language, documentRef.current?.id ?? null);
        const answer = (res?.answer || '').trim() || t(language, 'assistant_help');
        speakAnswer(answer);
      } catch {
        speakAnswer(t(language, 'error_generic'));
      }
    },
    [language, pushMessage, speakAnswer, speech]
  );

  const handleTranscript = useCallback(
    (transcript: string) => {
      const text = transcript.toLowerCase().trim();
      if (!text) return;

      if (containsAny(text, KEYWORDS.stop)) {
        stop();
        return;
      }
      if (containsAny(text, KEYWORDS.changeLanguage)) {
        onOpenSetup();
        return;
      }
      if (containsAny(text, KEYWORDS.read)) {
        pushMessage('user', transcript);
        readReport();
        return;
      }
      if (containsAny(text, KEYWORDS.upload)) {
        pushMessage('user', transcript);
        navigateAndSpeak('upload', 'nav_upload');
        return;
      }
      if (containsAny(text, KEYWORDS.timeline)) {
        pushMessage('user', transcript);
        navigateAndSpeak('timeline', 'nav_timeline');
        return;
      }
      if (containsAny(text, KEYWORDS.medicines)) {
        pushMessage('user', transcript);
        navigateAndSpeak('medications', 'nav_medications');
        return;
      }
      if (containsAny(text, KEYWORDS.comparison)) {
        pushMessage('user', transcript);
        navigateAndSpeak('comparison', 'nav_comparison');
        return;
      }
      if (containsAny(text, KEYWORDS.doctor)) {
        pushMessage('user', transcript);
        navigateAndSpeak('doctor-prep', 'nav_doctor');
        return;
      }
      if (containsAny(text, KEYWORDS.privacy)) {
        pushMessage('user', transcript);
        navigateAndSpeak('privacy-vault', 'nav_privacy');
        return;
      }
      if (containsAny(text, KEYWORDS.dashboard)) {
        pushMessage('user', transcript);
        navigateAndSpeak('dashboard', 'nav_dashboard');
        return;
      }

      // Anything else: understand the question and answer it out loud.
      ask(transcript);
    },
    [ask, navigateAndSpeak, onOpenSetup, pushMessage, readReport, stop]
  );

  const handleListenError = useCallback(
    (errCode: string) => {
      let key: TranslationKey;
      if (errCode === 'no-speech' || errCode === 'aborted') key = 'error_no_speech';
      else if (errCode === 'not-allowed' || errCode === 'service-not-allowed') key = 'error_mic_permission';
      else if (errCode === 'network') key = 'error_network';
      else key = 'error_generic';
      speakAnswer(t(language, key));
    },
    [language, speakAnswer]
  );

  const startListening = useCallback(() => {
    if (!speech.sttSupported) {
      speakAnswer(t(language, 'unsupported_voice'));
      return;
    }
    setStatus('listening');
    speech.listen((transcript) => handleTranscript(transcript), handleListenError);
  }, [handleListenError, handleTranscript, language, speakAnswer, speech]);

  // Hands-free: start listening again automatically once the assistant finishes.
  useEffect(() => {
    if (!handsFree || !isOpen) return;
    if (status === 'idle' && !speech.isListening && !speech.isSpeaking) {
      const timer = window.setTimeout(() => {
        if (handsFreeRef.current) startListening();
      }, 600);
      return () => window.clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, handsFree, isOpen, speech.isListening, speech.isSpeaking]);

  const openPanel = () => {
    setIsOpen(true);
    if (messages.length === 0) {
      setMessages([
        { id: nextId(), role: 'assistant', text: t(language, 'assistant_greeting') },
        { id: nextId(), role: 'assistant', text: t(language, 'assistant_help') }
      ]);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setStatus('idle');
  };

  const submitQuery = (e: React.FormEvent) => {
    e.preventDefault();
    const value = query;
    setQuery('');
    handleTranscript(value);
  };

  const quickActions = [
    { key: 'read' as const, icon: FileText, label: 'nav_explainer' as const },
    { key: 'upload' as const, icon: UploadCloud, label: 'nav_upload' as const },
    { key: 'medicines' as const, icon: Pill, label: 'nav_medications' as const },
    { key: 'comparison' as const, icon: GitCompare, label: 'nav_comparison' as const },
    { key: 'timeline' as const, icon: Clock, label: 'nav_timeline' as const },
    { key: 'doctor' as const, icon: Stethoscope, label: 'nav_doctor' as const }
  ];

  const runQuickAction = (key: string) => {
    if (key === 'read') {
      readReport();
      return;
    }
    const map: Record<string, { tab: string; label: Parameters<typeof t>[1] }> = {
      upload: { tab: 'upload', label: 'nav_upload' },
      timeline: { tab: 'timeline', label: 'nav_timeline' },
      medicines: { tab: 'medications', label: 'nav_medications' },
      comparison: { tab: 'comparison', label: 'nav_comparison' },
      doctor: { tab: 'doctor-prep', label: 'nav_doctor' },
      privacy: { tab: 'privacy-vault', label: 'nav_privacy' }
    };
    const target = map[key];
    if (target) navigateAndSpeak(target.tab, target.label);
  };

  const statusText =
    status === 'listening'
      ? t(language, 'listening')
      : status === 'thinking'
      ? t(language, 'thinking')
      : status === 'speaking'
      ? t(language, 'assistant_speaking')
      : t(language, 'speak_now');

  return (
    <>
      {/* Floating launcher */}
      {!isOpen && (
        <button
          onClick={openPanel}
          aria-label={t(language, 'voice_guide')}
          className="fixed bottom-5 right-5 z-50 flex items-center space-x-2 px-4 py-3.5 rounded-full bg-blue-700 hover:bg-blue-800 text-white shadow-xl shadow-blue-900/30 transition-all active:scale-95"
        >
          <span className="relative flex h-6 w-6 items-center justify-center">
            <Mic className="w-6 h-6" />
          </span>
          <span className="text-sm font-bold hidden sm:inline">{t(language, 'voice_guide')}</span>
        </button>
      )}

      {/* Assistant panel */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 z-50 w-[calc(100vw-2rem)] sm:w-96 max-h-[88vh] flex flex-col bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden">
          {/* Header */}
          <div className="bg-slate-900 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Activity className="w-4 h-4" />
              </div>
              <div>
                <div className="text-sm font-extrabold leading-tight">{t(language, 'assistant_name')}</div>
                <div className="text-[10px] text-slate-300">{t(language, 'voice_guide')} · {getLanguage(language).nativeLabel}</div>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setHandsFree((v) => !v)}
                className={`p-1.5 rounded-lg ${handsFree ? 'bg-blue-700 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
                title={handsFree ? t(language, 'voice_on') : t(language, 'voice_off')}
              >
                {handsFree ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              </button>
              <button
                onClick={clearConversation}
                className="p-1.5 rounded-lg text-slate-300 hover:bg-slate-800"
                title="Clear conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => { stop(); setIsOpen(false); }}
                className="p-1.5 rounded-lg text-slate-300 hover:bg-slate-800"
                aria-label="Close assistant"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Conversation */}
          <div className="flex-1 min-h-[120px] overflow-y-auto p-4 space-y-3 bg-slate-50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-sm leading-snug ${
                    msg.role === 'user'
                      ? 'bg-blue-700 text-white rounded-br-sm'
                      : 'bg-white text-slate-700 border border-slate-200 rounded-bl-sm'
                  }`}
                >
                  {msg.role === 'assistant' && (
                    <span className="block text-[10px] font-bold text-blue-700 mb-0.5">
                      {t(language, 'assistant_name')}
                    </span>
                  )}
                  {msg.text}
                </div>
              </div>
            ))}

            {status === 'thinking' && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 px-3.5 py-2.5 rounded-2xl bg-white border border-slate-200 text-sm text-slate-500">
                  <Loader2 className="w-4 h-4 text-amber-600 animate-spin" />
                  <span>{t(language, 'ai_thinking')}</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Status + controls */}
          <div className="p-4 space-y-3 border-t border-slate-100">
            <div className="flex items-center space-x-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  status === 'listening'
                    ? 'bg-red-500 animate-pulse'
                    : status === 'speaking'
                    ? 'bg-blue-600 animate-pulse'
                    : status === 'thinking'
                    ? 'bg-amber-500 animate-pulse'
                    : 'bg-slate-400'
                }`}
              />
              <span className="text-xs font-bold text-slate-700">{statusText}</span>
            </div>

            {speech.isSpeaking && (
              <button
                onClick={stop}
                className="w-full py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold"
              >
                {t(language, 'stop')}
              </button>
            )}

            <button
              onClick={speech.isListening ? stop : startListening}
              disabled={!speech.sttSupported}
              className={`w-full flex items-center justify-center space-x-2 py-3.5 rounded-2xl font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                speech.isListening ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-blue-700 hover:bg-blue-800 text-white'
              }`}
            >
              {speech.isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              <span>{speech.isListening ? t(language, 'stop') : t(language, 'speak_now')}</span>
            </button>

            {!speech.sttSupported && (
              <p className="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1.5">
                {t(language, 'unsupported_voice')}
              </p>
            )}

            {/* Type a question (works even without a microphone) */}
            <form onSubmit={submitQuery} className="flex items-center space-x-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t(language, 'ask_placeholder')}
                className="flex-1 min-w-0 px-3 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button
                type="submit"
                disabled={!query.trim()}
                aria-label={t(language, 'ask_send')}
                className="p-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            {/* Example prompts / shortcuts */}
            <div className="space-y-2">
              <div className="flex items-center space-x-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wide">
                <Sparkles className="w-3 h-3 text-blue-500" />
                <span>Try saying</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.key}
                      onClick={() => runQuickAction(action.key)}
                      className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-white border border-slate-200 hover:border-blue-300 hover:bg-blue-50 text-left text-[11px] font-semibold text-slate-700 transition-colors"
                    >
                      <Icon className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span className="truncate">{t(language, action.label)}</span>
                    </button>
                  );
                })}
                <button
                  onClick={onOpenSetup}
                  className="col-span-2 flex items-center justify-center space-x-2 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-[11px] font-bold text-slate-700 transition-colors"
                >
                  <Settings className="w-3.5 h-3.5 text-slate-500" />
                  <span>{t(language, 'redo_setup')}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
