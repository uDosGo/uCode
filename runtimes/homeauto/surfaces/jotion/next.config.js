/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@blocknote/react', '@blocknote/core', '@blocknote/mantine'],
  experimental: {
    optimizePackageImports: ['lucide-react', '@blocknote/react'],
  },
}

module.exports = nextConfig
