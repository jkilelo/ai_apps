import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ChartBarIcon,
    ComputerDesktopIcon,
    SparklesIcon,
    ArrowRightIcon,
    ClockIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline';

export function HomePage() {
    const features = [
        {
            title: 'Data Profiling & Quality Checks',
            description: 'Comprehensive data analysis with automated quality assessments, statistical profiling, and detailed reporting.',
            icon: ChartBarIcon,
            href: '/data-profiling',
            color: 'from-[#004685] to-blue-600',
            steps: ['Upload Data', 'Configure Profile', 'Run Analysis', 'Generate Report']
        },
        {
            title: 'Web Automation Flow',
            description: 'Automated UI testing and interaction workflows with intelligent element detection and validation.',
            icon: ComputerDesktopIcon,
            href: '/web-automation',
            color: 'from-[#004685] to-blue-700',
            steps: ['Define Target', 'Create Workflow', 'Execute Tests', 'Review Results']
        }
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
    };

    return (
        <div className="h-screen w-screen flex relative overflow-hidden fixed inset-0">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-slate-50 to-blue-100 dark:from-slate-900 dark:via-blue-900 dark:to-slate-800">
                <div className="absolute inset-0 opacity-40">
                    <div className="w-full h-full bg-repeat" style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23004685' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='10'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
                    }}></div>
                </div>

                {/* Floating Elements */}
                <motion.div
                    animate={{
                        rotate: [0, 360],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{
                        duration: 20,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-r from-[#004685]/20 to-blue-400/20 rounded-full blur-xl"
                />
                <motion.div
                    animate={{
                        rotate: [360, 0],
                        scale: [1, 0.8, 1],
                    }}
                    transition={{
                        duration: 15,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute bottom-20 left-20 w-24 h-24 bg-gradient-to-r from-blue-400/20 to-[#004685]/20 rounded-full blur-xl"
                />
            </div>

            {/* Main Content */}
            <div className="relative z-10 w-full h-full overflow-y-auto">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 min-h-full">
                    {/* Hero Section */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <div className="flex justify-center mb-6">
                            <div className="p-3 bg-gradient-to-r from-[#004685] to-blue-600 rounded-2xl shadow-lg">
                                <SparklesIcon className="h-8 w-8 text-white" />
                            </div>
                        </div>
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 dark:text-white mb-6">
                            AI-Powered
                            <span className="block bg-gradient-to-r from-[#004685] via-blue-600 to-[#004685] bg-clip-text text-transparent">
                                Data Platform
                            </span>
                        </h1>
                        <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
                            Transform your data workflows with intelligent automation. Perform comprehensive data profiling,
                            quality checks, and web automation with our modern, intuitive platform.
                        </p>
                    </motion.div>

                    {/* Feature Cards */}
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="grid md:grid-cols-2 gap-8 mb-16"
                    >
                        {features.map((feature) => {
                            const Icon = feature.icon;
                            return (
                                <motion.div
                                    key={feature.title}
                                    variants={itemVariants}
                                    whileHover={{ scale: 1.02 }}
                                    className="group"
                                >
                                    <Link to={feature.href}>
                                        <div className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-white/20 dark:border-slate-700/30 h-full">
                                            <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-r ${feature.color} mb-6`}>
                                                <Icon className="h-8 w-8 text-white" />
                                            </div>

                                            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 group-hover:text-[#004685] dark:group-hover:text-[#004685] transition-colors">
                                                {feature.title}
                                            </h3>

                                            <p className="text-slate-600 dark:text-slate-300 mb-6 leading-relaxed">
                                                {feature.description}
                                            </p>

                                            {/* Process Steps */}
                                            <div className="mb-6">
                                                <h4 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
                                                    Workflow Steps
                                                </h4>
                                                <div className="space-y-2">
                                                    {feature.steps.map((step, stepIndex) => (
                                                        <div key={stepIndex} className="flex items-center space-x-3">
                                                            <div className={`w-6 h-6 rounded-full bg-gradient-to-r ${feature.color} flex items-center justify-center`}>
                                                                <span className="text-white text-xs font-bold">{stepIndex + 1}</span>
                                                            </div>
                                                            <span className="text-sm text-slate-600 dark:text-slate-300">{step}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                                                    <ClockIcon className="h-4 w-4" />
                                                    <span>~5-10 minutes</span>
                                                </div>
                                                <div className="flex items-center space-x-2 text-[#004685] dark:text-[#004685] font-medium group-hover:translate-x-1 transition-transform">
                                                    <span>Get Started</span>
                                                    <ArrowRightIcon className="h-4 w-4" />
                                                </div>
                                            </div>
                                        </div>
                                    </Link>
                                </motion.div>
                            );
                        })}
                    </motion.div>

                    {/* Quick Stats */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/20 dark:border-slate-700/30"
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                            <div>
                                <div className="flex justify-center mb-3">
                                    <CheckCircleIcon className="h-8 w-8 text-[#004685]" />
                                </div>
                                <div className="text-3xl font-bold text-slate-900 dark:text-white mb-2">99.9%</div>
                                <div className="text-slate-600 dark:text-slate-300">Data Accuracy</div>
                            </div>
                            <div>
                                <div className="flex justify-center mb-3">
                                    <ClockIcon className="h-8 w-8 text-[#004685]" />
                                </div>
                                <div className="text-3xl font-bold text-slate-900 dark:text-white mb-2">&lt;5min</div>
                                <div className="text-slate-600 dark:text-slate-300">Average Processing</div>
                            </div>
                            <div>
                                <div className="flex justify-center mb-3">
                                    <SparklesIcon className="h-8 w-8 text-[#004685]" />
                                </div>
                                <div className="text-3xl font-bold text-slate-900 dark:text-white mb-2">AI-Powered</div>
                                <div className="text-slate-600 dark:text-slate-300">Smart Analysis</div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
