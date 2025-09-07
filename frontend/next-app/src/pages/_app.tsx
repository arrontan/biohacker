import type { AppProps } from 'next/app';
import Head from 'next/head';
import 'xterm/css/xterm.css';
import '../components/TerminalStyles.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <meta name="theme-color" content="#0b74de" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
