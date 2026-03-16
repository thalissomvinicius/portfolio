using System;
using Microsoft.Extensions.Configuration;
using Microsoft.Data.SqlClient;
using System.Data;

namespace TermosEContratosDesktop.Repositories
{
    public static class DatabaseConfig
    {
        public static string GetConnectionString()
        {
            var config = new ConfigurationBuilder()
                .SetBasePath(AppDomain.CurrentDomain.BaseDirectory)
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .Build();

            return config.GetConnectionString("DefaultConnection") 
                ?? throw new Exception("Connection string 'DefaultConnection' not found in appsettings.json.");
        }

        public static IDbConnection GetConnection()
        {
            return new SqlConnection(GetConnectionString());
        }
    }
}
