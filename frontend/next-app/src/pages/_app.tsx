import type { AppProps } from 'next/app';
import 'xterm/css/xterm.css';
import '../components/TerminalStyles.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
