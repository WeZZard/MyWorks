---
title: An Introduction to Gatsblog
subtitle: 'A Blog Built with Gatsby.js'
category: Showcase
tags: [Blog, Design, Programming, Gatsblog]
---

> This post has been revisited with LLM technology to improve its English
> fluency.

As mentioned in my Hello World post, no existing blog system fully meets my
needs, especially given my deep involvement with frontend technology.

This led me to create my own solution. This post documents my journey from
design to implementation, chronicling how an iOS developer with an
industrial design background ventured into modern frontend development.

## Pseudo-Live Editing

Gatsby.js provides a simple live editing feature. Launch Gatsby's
development server with `gatsby develop -H 0.0.0.0` or `npm run start`,
then open `http://localhost:8000` in your browser. Your post changes will
appear automatically when you save the edited file.

![Pseudo-Live Editing](./pseudo-live-editing.gif "Pseudo-Live Editing")

## Sophisticated Grid System

I implemented a sophisticated grid system with carefully tuned element
sizes and spacing. While the design may not be fancy, it
prioritizes functionality—ensuring content clarity and comfortable spacing
between elements.

## Responsive Image with Retina Display Support

Most figures in my posts are original creations, making it easy to
generate `@2x` and `@3x` versions alongside the original. Gatsby supports
resolution density through file naming conventions, recognizing image
series like `xxx.png`, `xxx@2x.png`, and `xxx@3x.png` as 1x, 2x, and 3x
resolution versions respectively. Simply use standard Markdown image
syntax:

```markdown
![Image Alternative Text](xxx.png "Image Title")
```

Gatsblog handles the responsiveness and Retina display support
automatically.

For images sourced from the web or cameras, providing multiple
resolution versions isn't always practical. Gatsblog handles this
gracefully—any single image file named `xxx.png` will receive responsive
support without requiring additional versions.

## KaTex

As a mathematics enthusiast, I've integrated KaTex support. Gatsby now
handles both inline expressions like `$$a^2 + b^2 = c^2$$` (rendered as
$$a^2 + b^2 = c^2$$) and block equations:

```katex
$$
\frac{1}{\Bigl(\sqrt{\phi \sqrt{5}}-\phi\Bigr) e^{\frac25 \pi}} \equiv 1+\frac{e^{-2\pi}} {1+\frac{e^{-4\pi}} {1+\frac{e^{-6\pi}} {1+\frac{e^{-8\pi}} {1+\cdots} } } }
$$
```

$$
\frac{1}{\Bigl(\sqrt{\phi \sqrt{5}}-\phi\Bigr) e^{\frac25 \pi}} \equiv 1+\frac{e^{-2\pi}} {1+\frac{e^{-4\pi}} {1+\frac{e^{-6\pi}} {1+\frac{e^{-8\pi}} {1+\cdots} } } }
$$

```katex
$$
\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)
$$
```

$$
\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)
$$

```katex
$$
\int u \frac{dv}{dx}\,dx=uv-\int \frac{du}{dx}v\,dx
$$
```

$$
\int u \frac{dv}{dx}\,dx=uv-\int \frac{du}{dx}v\,dx
$$

## Enhanced with MDX

### React Live

```javascript react-live
class Counter extends React.Component {
  constructor() {
    super();
    this.state = { count: 0 };
  }

  componentDidMount() {
    this.interval = setInterval(() => {
      this.setState(state => ({ count: state.count + 1 }));
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  render() {
    return (
      <center>
        <h3>{this.state.count}</h3>
      </center>
    );
  }
}
```

### Code Block with Path Label

Add `path=path_of_file` after the _language_ metadata in the fenced code
block's opening line:

```markdown
```c path=src/main.c
#include <stdio>

int main(int argc, char[] * args) {
    printf("Hello, world!\n");
    return 0;
}
​​```
```

This produces a code block with a path label:

```c path=src/main.c
#include <stdio>
int main(int argc, char[] * args) {
    printf("Hello, world!\n");
    return 0;
}
```

## Statically Deployed

Powered by Gatsby.js, Gatsblog supports static deployment. You can deploy
your site with just a few clicks on [Netlify](https://netlify.com).
