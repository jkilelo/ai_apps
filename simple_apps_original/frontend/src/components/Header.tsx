import { Search, Bell, Settings } from 'lucide-react';

const Header = () => {
    return (
        <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-lg">AI</span>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">Testing Platform</h1>
                            <p className="text-primary-100 text-sm">v1.0.0 - Data Profiling Module</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search..."
                                className="pl-10 pr-4 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-primary-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 w-64"
                            />
                        </div>

                        <button className="p-2 hover:bg-white hover:bg-opacity-10 rounded-lg transition-colors">
                            <Bell className="h-5 w-5" />
                        </button>

                        <button className="p-2 hover:bg-white hover:bg-opacity-10 rounded-lg transition-colors">
                            <Settings className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
