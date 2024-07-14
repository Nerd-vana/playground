import { Composition } from 'remotion';
import { MyComposition } from './Composition';
import './style.css';

export const RemotionRoot: React.FC = () => {
  // Default duration and fps
  const duration = 60; // Default to 60 seconds
  const fps = 30;

  const durationInFrames = Math.ceil(fps * duration);

  return (
    <>
      <Composition
        id="asciinema-player"
        component={MyComposition}
        durationInFrames={durationInFrames}
        fps={fps}
        width={1920}
        height={1080}
        defaultProps={{castPath: './macinstall.cast'}}
      />
    </>
  );
};