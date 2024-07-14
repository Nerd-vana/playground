import React, { useEffect, useRef } from 'react';
import asciinemaPlayer from 'asciinema-player';
import 'asciinema-player/dist/bundle/asciinema-player.css';

export const MyVideo: React.FC = () => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      asciinemaPlayer.create('/my_session.cast', ref.current, {
        cols: 80,
        rows: 24,
        autoPlay: true,
        loop: false,
        preload: true,
        theme: 'asciinema',
        speed: 1,
      });
    }
  }, []);

  return (
    <div ref={ref} style={{ width: '800px', height: '480px' }} />
  );
};
