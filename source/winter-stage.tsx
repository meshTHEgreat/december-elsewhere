import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import { useCallback, useEffect, useState, useSyncExternalStore } from 'react';
import { Stage } from '@winter/stageshow';
import type { Act } from '@winter/act';
import './winter-stage.css';

type Frame = { title: string; area: string; note: string; src: string };
type Scene = { index: number };
type Story = { label: string; frames: Frame[] };

const shallowViewport = window.matchMedia('(orientation: landscape) and (max-height: 28rem)');
const readShallow = () => shallowViewport.matches;
function watchShallow(update: () => void) {
  shallowViewport.addEventListener('change', update);
  return () => shallowViewport.removeEventListener('change', update);
}

function SceneFrame({story, index, report}: {story: Story; index: number; report: (index: number) => void}) {
  useEffect(() => { report(index); }, [index, report]);
  return <div className="wf-story-frame" data-story-index={index}>
    <div className="wf-story-image">
      {story.frames.map((frame, step) =>
        <img src={frame.src} alt="" decoding="async" key={frame.src}
          data-current={step === index ? 'yes' : 'no'} />)}
    </div>
    <div className="wf-story-editorial">
      <p className="wf-story-label">{story.label}</p>
      <div className="wf-story-words">
        {story.frames.map((frame, step) => <div key={frame.title} className="wf-story-beat"
          data-current={step === index ? 'yes' : 'no'} aria-hidden={step !== index}>
          <p className="wf-story-area">{frame.area}</p>
          <h3>{frame.title}</h3>
          <p className="wf-story-detail">{frame.note}</p>
        </div>)}
      </div>
      <ol className="wf-story-track" aria-label="Story progress">
        {story.frames.map((frame, step) => <li key={frame.title} aria-current={step === index ? 'step' : undefined} aria-label={frame.title}/>)}
      </ol>
    </div>
  </div>;
}

function Scenes({story}: {story: Story}) {
  const shallow = useSyncExternalStore(watchShallow, readShallow);
  const [picked, setPicked] = useState<number | null>(null);
  const [current, setCurrent] = useState(0);
  const initial = {index: 0};
  const poster = {index: story.frames.length - 1};
  const sequence = useCallback(async (a: Act<Scene>) => {
    const hold = story.frames.length === 3 ? 3400 : 2500;
    await a.wait(hold);
    for (let index = 1; index < story.frames.length; index++) {
      a.mark('beat-' + (index + 1));
      await a.set({index});
      await a.wait(index === story.frames.length - 1 ? 3400 : hold);
    }
  }, [story.frames.length]);

  return <>
    <Stage<Scene> width={shallow ? 460 : 736} height={shallow ? 190 : 338}
      compact={shallow ? undefined : {below: 654, width: 352, height: 365}}
      play="once" initial={initial} poster={poster} script={picked === null ? sequence : undefined}
      theme="dark" fidelity="realistic" accent="#f3d9a8"
      className={'wf-story' + (shallow ? ' wf-story--shallow' : '')} tokens={{'--ss-canvas':'#132621'}}>
      {state => <SceneFrame story={story} index={picked ?? state.index} report={setCurrent}/>}
    </Stage>
    <div className="wf-scene-controls" role="group" aria-label="Preview scenes">
      {story.frames.map((frame, index) => <button key={frame.title} type="button" className="action wf-scene-button"
        data-winter-scene={index} aria-pressed={(picked ?? current) === index}
        onClick={() => setPicked(index)}>{frame.title}</button>)}
    </div>
  </>;
}

export function mount(host: HTMLElement, story: Story) {
  const root = createRoot(host);
  flushSync(() => root.render(<Scenes story={story} />));
  return () => root.unmount();
}
