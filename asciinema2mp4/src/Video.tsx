import { Composition } from 'remotion';
import { MyVideo } from './MyVideo';

export const RemotionVideo: React.FC = () => {
  return (
    <>
      <Composition
        id="MyVideo"
        component={MyVideo}
        durationInFrames={1500} // Adjust according to your cast duration
        fps={30}
        width={800}
        height={480}
      />
    </>
  );
};
