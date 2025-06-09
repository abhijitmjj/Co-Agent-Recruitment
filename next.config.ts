import type {NextConfig} from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: false, // Set to false to ensure type checking during build
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'c.pxhere.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    // Aliasing handlebars to its runtime version to avoid webpack errors
    // See: https://github.com/handlebars-lang/handlebars.js/issues/1174
    // And: https://github.com/webpack/webpack/issues/1657
    config.resolve.alias = {
      ...config.resolve.alias,
      handlebars: 'handlebars/runtime',
    };

    // Suppress Critical dependency warning from Express
    // See: https://github.com/vercel/next.js/issues/12124#issuecomment-1030029315
    // And: https://webpack.js.org/configuration/other-options/#ignorewarnings
    config.ignoreWarnings = [
      ...(config.ignoreWarnings || []),
      {
        module: /express\/lib\/view\.js$/,
        message: /Critical dependency: the request of a dependency is an expression/,
      },
    ];

    return config;
  },
};

export default nextConfig;
