import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import { Stage } from '@winter/stageshow';
import type { Act } from '@winter/act';
import './winter-stage.css';

type Frame = { title: string; area: string; note: string; src: string };
type Scene = { index: number };
type Story = { label: string; frames: Frame[] };

function Scenes({ story }: { story: Story }) {
  const initial = {index: 0};
  const poster = {index: story.frames.length - 1};
  async function sequence(a: Act<Scene>) {
    const hold = story.frames.length === 3 ? 3400 : 2500;
    await a.wait(hold);
    for (let index = 1; index < story.frames.length; index++) {
      a.mark('beat-' + (index + 1));
      await a.set({index});
      await a.wait(index === story.frames.length - 1 ? 3400 : hold);
    }
  }
  return <Stage<Scene> width={736} height={338} compact={{below: 654, width: 352, height: 365}}
    play="once" initial={initial} poster={poster} script={sequence} theme="dark" fidelity="realistic"
    accent="#f3d9a8" className="wf-story" tokens={{'--ss-canvas':'#132621'}}>
    {state => <div className="wf-story-frame" data-story-index={state.index}>
      <div className="wf-story-image">
        {story.frames.map((frame, index) =>
          <img src={frame.src} alt="" decoding="async" key={frame.src}
            data-current={index === state.index ? 'yes' : 'no'} />)}
      </div>
      <div className="wf-story-editorial">
        <p className="wf-story-label">{story.label}</p>
        <div className="wf-story-words">
          {story.frames.map((frame, index) => <div key={frame.title} className="wf-story-beat"
            data-current={index === state.index ? 'yes' : 'no'} aria-hidden={index !== state.index}>
            <p className="wf-story-area">{frame.area}</p>
            <h3>{frame.title}</h3>
            <p className="wf-story-detail">{frame.note}</p>
          </div>)}
        </div>
        <ol className="wf-story-track" aria-label="Story progress">
          {story.frames.map((frame, index) => <li key={frame.title} aria-current={index === state.index ? 'step' : undefined} aria-label={frame.title}/>)}
        </ol>
      </div>
    </div>}
  </Stage>;
}

export function mount(host: HTMLElement, story: Story) {
  const root = createRoot(host);
  flushSync(() => root.render(<Scenes story={story} />));
  return () => root.unmount();
}
