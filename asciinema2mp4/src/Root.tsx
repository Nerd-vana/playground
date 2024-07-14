import { Composition } from 'remotion';
import { MyComposition } from './Composition';

import './style.css';

export const RemotionRoot: React.FC = () => {
	const duration = 20;
	const fps = 24;

	const durationInFrames = Math.ceil(fps * duration);

  return (
    <>
      <Composition
        id="asciinema-player"
        component={MyComposition}
        durationInFrames={durationInFrames}
        fps={fps}
        width={640}
        height={480}
      />
    </>
  );
};
