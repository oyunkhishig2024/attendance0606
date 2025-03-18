import UserCard from "@/components/UserCard";

const AdminPage = () => {
    return(
        <div className="p-4 gap-4 flex-col md:flex-row">
            {/* LEFT */}
            <div className="w-full lg:w-2/3"></div>


            {/* USER CARDS */}
            <div className="flex gap-4 justify-between flex-wrap">
                <UserCard type="student"/>
                <UserCard type="teacher"/>
                <UserCard type="parent"/>
                <UserCard type="staff"/>

            </div>


            {/* RIGHT */}
            <div className="w-full lg:w-1/3-"></div>

            {/* RIGHT */}
            <div className="w-full lg:w-1/3-"></div>

        </div>
    )
}

export default AdminPage;