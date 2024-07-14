import { Composition } from 'remotion';
import { MyComposition } from './Composition';
import { config } from '../config';

import './style.css';

export const RemotionRoot: React.FC = () => {

  const durationInFrames = Math.ceil(config.fps * config.duration);

  return (
    <>
      <Composition
        id="asciinema-player"
        component={MyComposition}
        durationInFrames={durationInFrames}
        fps={config.fps}
        width={config.width}
        height={config.height}
      />
    </>
  );
};
