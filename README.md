# Next.js + shadcn/ui + Tailwind CSS

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app) and configured with [shadcn/ui](https://ui.shadcn.com/) and [Tailwind CSS](https://tailwindcss.com/).

## 🚀 Getting Started

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🎨 Tech Stack

- **Next.js 15.5.4** - React framework with App Router
- **React 19** - Latest React version
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Utility-first CSS framework
- **shadcn/ui** - Re-usable components built with Radix UI and Tailwind CSS

## 📦 What's Included

- ✅ Next.js with App Router
- ✅ TypeScript configuration
- ✅ Tailwind CSS v4 setup
- ✅ shadcn/ui components (Button component included)
- ✅ ESLint configuration
- ✅ Dark mode support (via system preference)
- ✅ CSS variables for theming

## 🧩 Adding More shadcn/ui Components

To add more shadcn/ui components to your project:

```bash
# Add a specific component
npx shadcn@latest add [component-name]

# Examples:
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

Browse all available components at [ui.shadcn.com](https://ui.shadcn.com/)

## 📁 Project Structure

```
valids/
├── src/
│   ├── app/
│   │   ├── globals.css       # Global styles with theme variables
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page with button examples
│   ├── components/
│   │   └── ui/                # shadcn/ui components
│   │       └── button.tsx
│   └── lib/
│       └── utils.ts           # Utility functions (cn helper)
├── components.json            # shadcn/ui configuration
└── package.json
```

## 🎨 Customizing Theme

The theme colors are defined in `src/app/globals.css` using CSS variables. You can customize the color scheme by modifying the `--color-*` variables in both light and dark mode sections.

## 📚 Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Documentation](https://www.radix-ui.com/)

## 🚢 Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new).

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
