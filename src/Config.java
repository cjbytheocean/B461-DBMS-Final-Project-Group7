public class Config {
    static int PAGE_SIZE = 4096;
    static int BUFFER_POOL_SIZE = 8;
    static int BPLUS_ORDER = 4;
    static String DISK_FILE = "student_simulator.db";
    static String RESULTS_DIR = "results";
    static int RANDOM_SEED = 0;
    static int DEFAULT_NUM_RECORDS = 100;
    static int DEFAULT_NUM_QUERIES = 100;
    static int DEFAULT_PAGE_CAPACITY = 32;
    static double SEEK_COST = 0.05;
    static double TRANSFER_COST = 0.01;
    static double MEMORY_HIT_COST = 0.001;
}
