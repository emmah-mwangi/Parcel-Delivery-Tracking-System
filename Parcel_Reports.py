# Parcel Reports: sorting and statistics
import math

class Reports:
    def summary(self, parcels):
        total = len(parcels)
        statuses = {}
        weights = []
        distances = []
        for p in parcels:
            st = p.get('status', 'unknown')
            statuses[st] = statuses.get(st, 0) + 1
            try:
                weights.append(float(p.get('weight_kg', 0)))
            except Exception:
                pass
            try:
                distances.append(float(p.get('distance_km', 0)))
            except Exception:
                pass
        avg_weight = round(sum(weights) / len(weights), 2) if weights else 0
        avg_distance = round(sum(distances) / len(distances), 2) if distances else 0
        return {
            'total_parcels': total,
            'by_status': statuses,
            'average_weight_kg': avg_weight,
            'average_distance_km': avg_distance
        }

    def top_destinations(self, parcels, limit=5):
        counts = {}
        for p in parcels:
            d = p.get('destination', 'unknown')
            counts[d] = counts.get(d, 0) + 1
        sorted_dest = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{'destination': d, 'count': c} for d, c in sorted_dest[:limit]]

    def weight_distribution(self, parcels):
        bins = [0,5,10,20,50,100]
        dist = {f"{bins[i]}-{bins[i+1]}": 0 for i in range(len(bins)-1)}
        dist[ f">={bins[-1]}" ] = 0
        for p in parcels:
            try:
                w = float(p.get('weight_kg', 0))
            except Exception:
                continue
            placed = False
            for i in range(len(bins)-1):
                if bins[i] <= w < bins[i+1]:
                    dist[f"{bins[i]}-{bins[i+1]}"] += 1
                    placed = True
                    break
            if not placed:
                dist[f">={bins[-1]}"] += 1
        return dist
