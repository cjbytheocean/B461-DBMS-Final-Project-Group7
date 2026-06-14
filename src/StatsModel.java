import java.util.HashMap;

public record StatsModel(int reads, int writes, int deletes, int hits, int misses, int evictions, int flushes, double simulatedTimeMs, double elapsedSeconds) {
    public HashMap<String, Double> toDict() {
        HashMap<String, Double> map = new HashMap<>();
        map.put("reads", (double) reads);
        map.put("writes", (double) writes);
        map.put("deletes", (double) deletes);
        map.put("hits", (double) hits);
        map.put("misses", (double) misses);
        map.put("evictions", (double) evictions);
        map.put("flushes", (double) flushes);
        map.put("simulated_time_ms", simulatedTimeMs);
        map.put("elapsed_seconds", elapsedSeconds);
        return map;
    }
}
