//! OBF Reference — Open Bridge Format directives, segments, examples

use crate::DocSection;

/// Generate the OBF reference documentation
pub fn generate() -> DocSection {
    DocSection {
        title: "OBF Reference".into(),
        content: "OBF (Open Bridge Format) is a Markdown-based scene definition language for home automation.".into(),
        subsections: vec![
            DocSection {
                title: "Directives".into(),
                content: "Directives are prefixed with `@` and define the scene metadata.".into(),
                subsections: vec![
                    DocSection {
                        title: "@spec".into(),
                        content: "Defines the OBF specification version.\n\n```markdown\n# @spec version=1.0\n```\n\nRequired. Must be the first directive.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@target".into(),
                        content: "Specifies the target system for execution.\n\n```markdown\n# @target: homenest-console\n```\n\nSupported targets: `homenest-console`, `homeassistant`, `cli`.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@ha".into(),
                        content: "Home Assistant service call.\n\n```markdown\n- @ha:scene.movie_mode\n- @ha:light.living_room?brightness=50&color_temp=4000\n- @ha:climate.living_room?temperature=68\n- @ha:media_player.living_room?source=HDMI\n```\n\nFormat: `@ha:<domain>.<entity_id>?<param1>=<value1>&<param2>=<value2>`".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@media".into(),
                        content: "Media playback action.\n\n```markdown\n- @media:play?media_id=movie/123\n- @media:resume?position=last\n- @media:volume?level=65\n- @media:pause\n- @media:stop\n```\n\nSupported actions: `play`, `resume`, `pause`, `stop`, `volume`, `seek`.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@delay".into(),
                        content: "Delays execution of subsequent actions.\n\n```markdown\n- @delay:duration=30s\n- @delay:duration=5m\n- @delay:duration=1h\n- @delay:duration=movie\n```\n\nSupported units: `s` (seconds), `m` (minutes), `h` (hours).\nSpecial value `movie` waits for the current media to finish.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@tv".into(),
                        content: "TV/DVR action.\n\n```markdown\n- @tv:channel?number=7\n- @tv:record?channel=ABC&duration=60m\n- @tv:guide\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "@voice".into(),
                        content: "Voice assistant action.\n\n```markdown\n- @voice:say?text=Movie+night+starting\n- @voice:listen?timeout=10s\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Segments".into(),
                content: "Segments organize actions into logical groups using Markdown headings.".into(),
                subsections: vec![
                    DocSection {
                        title: "Segment Structure".into(),
                        content: "```markdown\n## Environment Setup\n- @ha:scene.movie_mode\n- @ha:climate.living_room?temperature=68\n\n## Media Playback\n- @media:resume?position=last\n- @media:volume?level=65\n\n## Delayed Actions\n- @delay:duration=movie\n- @ha:light.living_room?brightness=50\n```\n\nSegments execute in order. Each segment completes before the next begins.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Conditional Segments".into(),
                        content: "Segments can have conditions:\n\n```markdown\n## Evening Setup\n# @if:time=after_sunset\n- @ha:light.living_room?brightness=30\n- @ha:cover.living_room?position=closed\n\n## Morning Setup\n# @if:time=before_noon\n- @ha:light.living_room?brightness=80\n- @ha:cover.living_room?position=open\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Examples".into(),
                content: "Complete OBF scene examples.".into(),
                subsections: vec![
                    DocSection {
                        title: "Movie Night".into(),
                        content: "```markdown\n# OBF: Movie Night\n# @spec version=1.0\n# @target: homenest-console\n\n## Environment Setup\n- @ha:scene.movie_mode\n- @ha:light.living_room?brightness=20\n- @ha:climate.living_room?temperature=68\n\n## Media Playback\n- @media:resume?position=last\n- @media:volume?level=65\n\n## Delayed Actions\n- @delay:duration=movie\n- @ha:light.living_room?brightness=80\n- @ha:scene.evening\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Goodnight".into(),
                        content: "```markdown\n# OBF: Goodnight\n# @spec version=1.0\n# @target: homenest-console\n\n## Shutdown\n- @media:stop\n- @ha:scene.goodnight\n- @ha:light.*?brightness=0\n- @ha:climate.bedroom?temperature=65\n\n## Confirm\n- @delay:duration=30s\n- @ha:lock.front_door?lock=true\n- @voice:say?text=Goodnight\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Morning Routine".into(),
                        content: "```markdown\n# OBF: Morning\n# @spec version=1.0\n# @target: homenest-console\n\n## Wake Up\n- @ha:light.bedroom?brightness=60\n- @ha:climate.home?temperature=70\n- @media:play?media_id=playlist/morning\n\n## Kitchen\n- @delay:duration=5m\n- @ha:coffee_maker.brewer?turn_on=true\n- @voice:say?text=Coffee+is+ready\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
        ],
    }
}
