"""
REPORTS MODULE
================
Read-only statistics computed over the parcel array. Nothing here
mutates state - it just summarises it for the dashboard / reports tab.
"""


class Reports:
    def summary(self, parcels):
        total = len(parcels)
        statuses = {}
        weights = []
        revenue = 0

        for p in parcels:
            status = p.get('status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
            try:
                weights.append(float(p.get('weight_kg', 0)))
            except (TypeError, ValueError):
                pass
            revenue += p.get('cost', 0) or 0

        avg_weight = round(sum(weights) / len(weights), 2) if weights else 0

        return {
            'total_parcels': total,
            'by_status': statuses,
            'average_weight_kg': avg_weight,
            'total_revenue': round(revenue, 2)
        }

    def top_destinations(self, parcels, limit=5):
        counts = {}
        for p in parcels:
            dest = p.get('delivery_type', 'Unknown')
            counts[dest] = counts.get(dest, 0) + 1
        ranked = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
        return [{'destination': d, 'count': c} for d, c in ranked[:limit]]

    def weight_distribution(self, parcels):
        bins = [0, 5, 10, 20, 50, 100]
        labels = [f"{bins[i]}-{bins[i+1]}kg" for i in range(len(bins) - 1)]
        labels.append(f">={bins[-1]}kg")
        distribution = {label: 0 for label in labels}

        for p in parcels:
            try:
                w = float(p.get('weight_kg', 0))
            except (TypeError, ValueError):
                continue
            placed = False
            for i in range(len(bins) - 1):
                if bins[i] <= w < bins[i + 1]:
                    distribution[labels[i]] += 1
                    placed = True
                    break
            if not placed:
                distribution[labels[-1]] += 1

        return distribution

    def queue_status(self, priority_queue):
        ordered = priority_queue.to_ordered_list()
        next_up = ordered[0] if ordered else None
        return {
            'waiting': len(ordered),
            'next_tracking_number': next_up.get('tracking_number') if next_up else None
        }
